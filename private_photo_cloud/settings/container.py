import dj_database_url

from .defaults import *

DATABASES['default'] = dj_database_url.config(conn_max_age=600)
