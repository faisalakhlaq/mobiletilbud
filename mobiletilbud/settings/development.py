from .base import *

DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1']

try:
   from .local import *
except:
   pass

if not SECRET_KEY: 
    import os
    SECRET_KEY = os.environ.get('SECRET_KEY')

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'staticfiles'
]
STATIC_ROOT = BASE_DIR / 'cdn_test' / 'static'
# Any file field upload goes here by default
MEDIA_ROOT = BASE_DIR / 'cdn_test' / 'media'
MEDIA_URL = '/media/'

if DEBUG:
    STATIC_ROOT.mkdir(parents=True, exist_ok=True)
    MEDIA_ROOT.mkdir(parents=True, exist_ok=True)

# CELERY
CELERY_BROKER_URL = 'redis://localhost:6379'
CELERY_TIMEZONE = 'Europe/Copenhagen'
