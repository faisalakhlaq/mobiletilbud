from .base import *

DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1']
SECRET_KEY = None

try:
    from .local import *
except:
   pass

# Check if we don't have secret and database 
# then create new to be used for CI in GitHub.
# This happens because we are not commiting the
# local settings file to github. We need these 
# values to run our tests
if not SECRET_KEY: 
    SECRET_KEY = env('SECRET_KEY')
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': 'test_db',
            # 'TEST': {
            #     'NAME': 'test_db',
            # },
        }
    }

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
