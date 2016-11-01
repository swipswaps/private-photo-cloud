import dj_database_url

from .factory_defaults import *

DATABASES['default'] = dj_database_url.config(conn_max_age=600)

INSTALLED_APPS += [
    'storage',
]

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
STATIC_ROOT = os.path.join(BASE_DIR, 'static_collected')

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
