from rest_framework import routers

from catalog import rest_views

router = routers.DefaultRouter()
router.register(r'media', rest_views.MediaViewSet)
router.register(r'm', rest_views.MViewSet)
