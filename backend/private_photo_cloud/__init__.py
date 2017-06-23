# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.

try:
    from .celery import app as celery_app
except:
    pass

__all__ = ['celery_app']
