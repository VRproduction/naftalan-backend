from .base import *

DEBUG = True

ALLOWED_HOSTS = ["*"]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

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

SITE_URL='http://localhost:8000'
SITE_NAME='Kurort Naftalan'


import os

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,  # Mevcut logger'ları devre dışı bırakma
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'django_errors.log'),
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',  # ERROR yerine INFO seviyesi
            'propagate': False,
        },
        'django.request': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'DEBUG',  # SQL sorgularını görmek için
            'propagate': False,
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}