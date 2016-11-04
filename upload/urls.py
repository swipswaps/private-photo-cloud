from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^$', views.upload),
    url(r'^file/$', views.upload_file),
    url(r'^check[-]present[-](?P<alg>sha1)/(?P<digest>[0-9a-f]{40})$', views.check_present),
]
