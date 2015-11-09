find .. \
    -not \( -path '../venv' -prune \) \
    -not \( -path '../*/migrations' -prune \) \
    -not \( -name '__init__.py' \) \
    -not \( -name 'manage.py' \) \
    -not \( -name 'populate.py' \) \
    -name '*.py' \
    -exec echo '>>> ' {} \; \
    -exec pep8 {} \;
