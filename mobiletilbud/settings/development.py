from .base import *

DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1']


# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }
try:
   from .local import *
except:
   pass

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

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
