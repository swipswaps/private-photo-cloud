from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^$', views.upload),
    url(r'^file/$', views.upload_file),
    url(r'^media/(?P<alg>sha1)_(?P<digest>[0-9a-f]{40})_(?P<size>\d+)/$', views.check_present),
]
