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



CELERY_RESULT_BACKEND = 'django-db'
CELERY_BROKER_URL='redis://localhost:6379/4'
CELERY_ACCEPT_CONTENT=['application/json']
CELERY_RESULT_SERIALIZER='json'
CELERY_TASK_SERIALIZER='json'

SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
X_FRAME_OPTIONS = 'DENY'

CELERY_BEAT_SCHEDULER='django_celery_beat.schedulers:DatabaseScheduler'

SITE_URL='https://adminnn.kurortnaftalan.com'
SITE_NAME='Kurort Naftalan'



LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'django_errors.log'),
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}