from .base import *

DEBUG = False
TEMPLATES[0]['OPTIONS']['debug'] = False
SECRET_KEY = env('DJANGO_SECRET_KEY', default='6_nmfhb8jto6u=!h3*s+@84#rf51=3cx$y6z--z@&!8mj2-(eo')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'test_db',
        'USER': env('POSTGRES_USER', default='postgres'),
        'PASSWORD': env('POSTGRES_PASSWORD', default=''),
        'ATOMIC_REQUESTS': True
    }
}

EMAIL_HOST = 'localhost'
EMAIL_PORT = 1025
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': ''
    }
}

TEST_RUNNER = 'django.test.runner.DiscoverRunner'

# Use fast password hasher so tests run faster
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Keep templates in memory so tests run faster
TEMPLATES[0]['OPTIONS']['loaders'] = [
    ['django.template.loaders.cached.Loader', [
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    ], ],
]
