from .base import *

DEBUG = False

ALLOWED_HOSTS = ['ip-address', 'www.mobiletilbud.dk']

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'mobiletilbud-db',
        'USER': 'db-user',
        'PASSWORD': 'db-user-password',
        'HOST': 'localhost',
        'PORT': '',
    }
}

try:
   from .local import *
except:
   pass
