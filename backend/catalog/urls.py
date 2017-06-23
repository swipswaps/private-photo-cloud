from django.conf.urls import url, include

from .rest_router import router
from . import views

app_name = 'catalog'

urlpatterns = [
    url(r'^$', views.catalog, name='list'),
    url(r'^images/months[.]json', views.images_months),
    url(r'^images/(?P<year>\d{4})-(?P<month>0[1-9]|1[0-2])[.]json', views.images_for_month),

    url(r'^api/', include(router.urls)),
]
