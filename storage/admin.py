from django.contrib import admin

from . import models

admin.site.register(models.Shot)
admin.site.register(models.Photo)
admin.site.register(models.Video)
