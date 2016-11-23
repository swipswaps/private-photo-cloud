from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^$', views.catalog),
    url(r'^images/months[.]json', views.images_months),
    url(r'^images/(?P<year>\d{4})-(?P<month>0[1-9]|1[0-2])[.]json', views.images_for_month),
]
