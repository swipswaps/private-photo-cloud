"""private_photo_cloud URL Configuration"""

from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView
from django.conf import settings
from django.conf.urls.static import static
from django.views.i18n import JavaScriptCatalog

urlpatterns = [
    url(r'^login/', LoginView.as_view(), name='login'),
    url(r'^logout/', LogoutView.as_view(), name='logout'),

    url(r'^api/auth/', include('rest_framework.urls', namespace='rest_framework')),

    # JS translations (djangojs domain) -- for given package(s) only
    url(r'^jsi18n/(?P<packages>\S+?).js$', JavaScriptCatalog.as_view(), name='javascript-catalog'),

    url(r'^admin/', admin.site.urls),

    url(r'^upload/', include('upload.urls', namespace='upload')),
    url(r'^', include('catalog.urls', namespace='catalog')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)   # it works only with DEBUG=True
