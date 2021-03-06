import os
import dj_database_url
import django_cache_url
import dj_email_url

from .factory_defaults import *

DEBUG = (os.environ.get('DJANGO_DEBUG') == '1')
TEMPLATES[0]['OPTIONS']['debug'] = (os.environ.get('DJANGO_TEMPLATE_OPTIONS_DEBUG') == '1')

# TODO: Investigate why connections leak with PostgreSQL-alpine + Python 3.6.0rc1 + Django pre-1.11: conn_max_age=600
DATABASES['default'] = dj_database_url.config()

CACHES = {
    'default': django_cache_url.config(),
    'persistent': django_cache_url.parse(os.environ.get('CACHE_PERSISTENT_URL')),
}

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "persistent"

locals().update(dj_email_url.config())

# pip install tzlocal
# from tzlocal import get_localzone
# TIME_ZONE = get_localzone().zone
TIME_ZONE = 'UTC'   # Inside container is always UTC

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'channels', # we must disable ASGI for main upload flow and use it for WebSockets only (slow, no huge files)
    'rest_framework',
    'crispy_forms',
    'django.contrib.postgres',
    # 'django.contrib.gis', # TODO: Install and enable

    'storage',
    'upload',
    'catalog',
    'processing',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.locale.LocaleMiddleware',    # Recognize and switch language by request headers
]

CHANNEL_LAYERS = {
    "default": {
#        "BACKEND": "asgi_ipc.IPCChannelLayer",  # it is incredibly slow
        "BACKEND": "asgi_redis.RedisChannelLayer",
        "CONFIG": {
            "hosts": [
                (os.environ.get('CHANNEL_REDIS_HOST'), int(os.environ.get('CHANNEL_REDIS_PORT')))
            ],
        },
        "ROUTING": "private_photo_cloud.routing.channel_routing",
    },
}

# Celery settings

CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL')
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_URL')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'

# Since auto-discovery crashes -- list all modules with tasks
CELERY_IMPORTS = [
    'upload.tasks',
    'processing.tasks',
]


MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_URL = '/static/'
MEDIA_URL = '/media/'

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = '/'

TEMPLATES[0]['DIRS'] = [
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

WS_PORT = int(os.environ.get('DJANGO_WS_PORT') or '80', 10)

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated'
    ],
    'PAGE_SIZE': 100,
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
}

import yaml

locals().update({k[7:]: yaml.safe_load(v) for k, v in os.environ.items() if k.startswith('DJANGO_')})
