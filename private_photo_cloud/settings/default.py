import dj_database_url

from .factory_defaults import *

DATABASES['default'] = dj_database_url.config(conn_max_age=600)

INSTALLED_APPS += [
    'photo',
]

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
