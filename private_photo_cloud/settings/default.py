import os
import dj_database_url

from .factory_defaults import *

DEBUG = (os.environ.get('DJANGO_DEBUG') == '1')
TEMPLATES[0]['OPTIONS']['debug'] = (os.environ.get('DJANGO_TEMPLATE_DEBUG') == '1')


DATABASES['default'] = dj_database_url.config(conn_max_age=600)

INSTALLED_APPS += [
    'storage',
    'upload',
]

# Celery settings

CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL')
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_URL')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'

# Since auto-discovery crashes -- list all modules with tasks
CELERY_IMPORTS = [
    'upload.tasks',
]


TIME_ZONE = 'Europe/Berlin'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
STATIC_ROOT = os.path.join(BASE_DIR, 'static_collected')
STATIC_URL = '/static/'
MEDIA_URL = '/media/'

LOGIN_URL = 'login'

TEMPLATES[0]['DIRS'] += [
    os.path.join(BASE_DIR, 'templates'),
]

TEMPLATES[0]['OPTIONS']['context_processors'] = [
    'django.template.context_processors.debug',
    'django.template.context_processors.request',
    'django.contrib.auth.context_processors.auth',
    'django.contrib.messages.context_processors.messages',
    'django.template.context_processors.i18n',
    'django.template.context_processors.media',
    'django.template.context_processors.static',
    'django.template.context_processors.csrf',
    'django.template.context_processors.tz',
]

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(asctime)s %(levelname)s %(message)s'
        },
    },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
    },
    'loggers': {
        '': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'storage': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    }
}