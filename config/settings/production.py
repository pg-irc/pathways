import logging
from .base import *

# Raises ImproperlyConfigured exception if DJANGO_SECRET_KEY not in os.environ
SECRET_KEY = env('DJANGO_SECRET_KEY')

# Ensure that Django will be able to detect a secure connection properly on Heroku.
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

WHITENOISE_MIDDLEWARE = ['whitenoise.middleware.WhiteNoiseMiddleware', ]
MIDDLEWARE = WHITENOISE_MIDDLEWARE + MIDDLEWARE

# See https://docs.djangoproject.com/en/dev/ref/middleware/#module-django.middleware.security
# and https://docs.djangoproject.com/en/dev/howto/deployment/checklist/#run-manage-py-check-deploy

# set this to 60 seconds and then to 518400 when you can prove it works
SECURE_HSTS_SECONDS = 60
SECURE_HSTS_INCLUDE_SUBDOMAINS = env.bool('DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS', default=True)
SECURE_CONTENT_TYPE_NOSNIFF = env.bool('DJANGO_SECURE_CONTENT_TYPE_NOSNIFF', default=True)
SECURE_BROWSER_XSS_FILTER = True
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SECURE_SSL_REDIRECT = env.bool('DJANGO_SECURE_SSL_REDIRECT', default=True)
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
X_FRAME_OPTIONS = 'DENY'
ALLOWED_HOSTS = env.list('DJANGO_ALLOWED_HOSTS', default=['fierce-ravine-89308.herokuapp.com', ])
INSTALLED_APPS += ['gunicorn', 'storages', ]
AWS_STORAGE_BUCKET_NAME = env('DJANGO_AWS_STORAGE_BUCKET_NAME')
MEDIA_URL = 'https://s3.amazonaws.com/%s/' % AWS_STORAGE_BUCKET_NAME
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

TEMPLATES[0]['OPTIONS']['loaders'] = [
    ('django.template.loaders.cached.Loader', [
        'django.template.loaders.filesystem.Loader', 'django.template.loaders.app_directories.Loader', ]),
]

DATABASES = {
    'default': env.db('DATABASE_URL')
}

DATABASES['default']['CONN_MAX_AGE'] = env.int('CONN_MAX_AGE', default=60)
