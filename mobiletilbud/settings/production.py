import os
from .base import *

DEBUG = False

SECRET_KEY = os.getenv("SECRET_KEY")

ALLOWED_HOSTS = ['www.mobiletilbud.dk']

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

# Ponanywhere MySQL DB
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv("DB_NAME"),
        'USER': os.getenv("DB_USER"),
        'PASSWORD': os.getenv("DB_PASSWORD"),
        'HOST': os.getenv("DB_HOST"),
        'PORT': os.getenv("DB_PORT"),
    }
}

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'staticfiles'
]
STATIC_ROOT = BASE_DIR / 'static'
# Any file field upload goes here by default
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
