import os
import requests
import threading
from PIL import Image

from django.core.files.storage import FileSystemStorage
from django.conf import settings


class OverwriteStorage(FileSystemStorage):
    """ Provide filename for uploads """

    def __init__(self, *args, **kwargs):
        super().__init__(*args,
                         location=settings.AVATARS_ROOT,
                         **kwargs)

    def get_available_name(self, name):
        if self.exists(name):
            os.remove(os.path.join(settings.AVATARS_ROOT, name))
        return name


def avatar_filename(instance, filename):
    """ Filename for avatars """
    return instance.username + '.jpg'


def image_resize(img_input, img_output, max_size):
    """
    Resizes input image so that longest side is equal to max_size
    img_input, img_output - pathes for input and output files
    max_size - length in pixels
    """

    # Read file
    image = Image.open(img_input).convert('RGB')
    image_size = image.size

    # Resize
    ratio = max_size / max(image_size[0], image_size[1])
    new_size = (int(image_size[0]*ratio), int(image_size[1]*ratio))
    image = image.resize(new_size, Image.ANTIALIAS)

    # Save to disk
    image.save(img_output, format='JPEG')

    return image


def get_ip(request):
    """
    Get client's IP
    """

    real_ip = request.META.get('HTTP_X_REAL_IP')
    # Proxy
    if real_ip:
        ip = real_ip
    # No proxy
    else:
        ip = request.META.get('REMOTE_ADDR')

    return ip


def get_location(ip):
    """
    Get client's geo info in JSON
    Sample:
        ip: 10.10.10.10,
        country_code: XX,
        country_name: Country,
        region_code: YYY,
        region_name: State name,
        city: City,
        zip_code: 123456,
        time_zone: Region/Zone,
        latitude: 10.123,
        longitude: 10.123,
        metro_code: 0
    """

    # TODO: remove after testing
    ip = '128.70.126.226'
    result = {}
    try:
        response = requests.get('http://freegeoip.net/json/'+ip)
    except requests.ConnectionError:
        result['error'] = 'Connection error'
    except requests.Timeout:
        result['error'] = 'Connection timeout'
    except requests.HTTPError:
        result['error'] = 'Invalid response'
    else:
        if response.status_code == 200:
            json = response.json()
            if 'latitude' not in json and 'longitude' not in json:
                result['error'] = 'No geo info available'
            else:
                result = json
        else:
            result['error'] = 'Bad request'

    return result


class UpdateGeo(threading.Thread):
    """
    Save geo info to the database model
    """

    def __init__(self, model, ip, **kwargs):
        self.model = model
        self.ip = ip
        super(UpdateGeo, self).__init__(**kwargs)

    def run(self):
        info = get_location(self.ip)
        if 'error' in info:
            return False
        else:
            for attr in info:
                setattr(self.model, attr, info[attr])
            self.model.save()
            return True