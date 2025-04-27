import os

from .base import *

DEBUG = False

ALLOWED_HOSTS = [
   "*"
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql_psycopg2',
#         'NAME': os.getenv('DB_APP'),
#         'USER': os.getenv('DB_USER'),
#         'PASSWORD': os.getenv('DB_PASSWORD'),
#         'HOST': os.getenv("DB_HOST"),
#         'PORT': os.getenv("DB_PORT"),
#     }
# }

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False
EMAIL_HOST_USER = 'ilqarhsnzad@gmail.com'
EMAIL_HOST_PASSWORD = 'nfpygvxpvwitdjka'
DEFAULT_FROM_EMAIL = 'ilqarhsnzad@gmail.com'



CELERY_BROKER_URL = 'redis://localhost:6379/4'
CELERY_RESULT_BACKEND = 'django-db'


INTERNAL_IPS = [
    "127.0.0.1",
]

SITE_URL='http://75.119.147.165:59/'
SITE_NAME='NAFTALAN-KURORT'