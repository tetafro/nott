import bleach
import json
import logging

from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.models import Count
from django.http import JsonResponse
from django.views.generic import View

from core.api import ApiView, get_token
from apps.admin.models import Config
from .models import User, Token
from .helpers import generate_token


class LoginView(View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body.decode('utf-8'))
        username = bleach.clean(data.get('username'))
        password = bleach.clean(data.get('password'))

        user = authenticate(username=username, password=password)

        if user is None:
            return JsonResponse(
                {'error': 'wrong username or password'}, status=400
            )

        try:
            token = Token.objects.create(string=generate_token(), user=user)
            token.save()
        except (IntegrityError, ValidationError) as e:
            logging.error('Failed to create token: %s', e)
            return JsonResponse({}, status=500)

        return JsonResponse({'token': token.string}, status=200)


class RegisterView(View):
    def post(self, request, *args, **kwargs):
        try:
            db_setting = Config.objects.get(code='allow_registration')
        except Config.DoesNotExist:
            reg_allowed = True  # default if settings is not found
        else:
            reg_allowed = db_setting.value == 'true'

        if not reg_allowed:
            return JsonResponse(
                {'error': 'registration is currently disabled'},
                status=400
            )

        data = json.loads(request.body.decode('utf-8'))
        username = bleach.clean(data.get('username'))
        email = bleach.clean(data.get('email'))
        password1 = bleach.clean(data.get('password1'))
        password2 = bleach.clean(data.get('password2'))

        if password1 != password2:
            return JsonResponse(
                {'error': 'passwords do not match'},
                status=400
            )

        # Create user
        # TODO: validate email format
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password1
            )
            user.save()
        except IntegrityError:
            return JsonResponse(
                {'error': 'username or email is already taken'},
                status=400
            )

        # Sign in created user
        try:
            token = Token.objects.create(
                string=generate_token(),
                user=user
            )
            token.save()
        except (IntegrityError, ValidationError) as e:
            logging.error('Failed to create token: %s', e)
            return JsonResponse({}, status=500)

        return JsonResponse({'token': token.string}, status=200)


class LogoutView(View):
    def post(self, request, *args, **kwargs):
        token = get_token(request)
        print(token)
        try:
            Token.objects.get(string=token).delete()
            return JsonResponse({}, status=200)
        except Token.DoesNotExist:
            return JsonResponse({'error': 'Invalid token'}, status=400)


class UserView(ApiView):
    def list(self, request, *args, **kwargs):
        users = User.objects.\
            annotate(folders_count=Count(
                'folders',
                distinct=True
            )).\
            annotate(notepads_count=Count(
                'folders__notepads',
                distinct=True
            )).\
            annotate(notes_count=Count(
                'folders__notepads__notes',
                distinct=True
            )).\
            all()
        response = {'users': [u.to_dict() for u in users]}
        return JsonResponse(response)

    def get(self, request, *args, **kwargs):
        user_id = kwargs.get('id')

        try:
            # Get user's stats
            user = User.objects.\
                annotate(folders_count=Count(
                    'folders',
                    distinct=True
                )).\
                annotate(notepads_count=Count(
                    'folders__notepads',
                    distinct=True
                )).\
                annotate(notes_count=Count(
                    'folders__notepads__notes',
                    distinct=True
                )).\
                get(id=user_id)
        except User.DoesNotExist:
            response = {'error': 'Object not found'}
            return JsonResponse(response, status=404)

        response = user.to_dict()
        return JsonResponse(response, status=200)

    def put(self, request, *args, **kwargs):
        user_id = kwargs.get('id')

        try:
            # Get user's stats
            user = User.objects.\
                annotate(folders_count=Count(
                    'folders',
                    distinct=True
                )).\
                annotate(notepads_count=Count(
                    'folders__notepads',
                    distinct=True
                )).\
                annotate(notes_count=Count(
                    'folders__notepads__notes',
                    distinct=True
                )).\
                get(id=user_id)
        except User.DoesNotExist:
            response = {'error': 'Object not found'}
            return JsonResponse(response, status=404)

        # TODO: Update user

        response = user.to_dict()
        return JsonResponse(response, status=200)
