"""private_photo_cloud URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView
from django.conf import settings
from django.conf.urls.static import static
from django.views.i18n import JavaScriptCatalog

urlpatterns = [
    url(r'^login/', LoginView.as_view(), name='login'),
    url(r'^logout/', LogoutView.as_view(), name='logout'),
    url(r'^admin/', admin.site.urls),
    url(r'^upload/', include('upload.urls', namespace='upload')),

    # Override domain to use the same django.po file, not djangojs.po
    url(r'^jsi18n/$', JavaScriptCatalog.as_view(domain='django'), name='javascript-catalog'),

    url(r'^', include('catalog.urls', namespace='catalog')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
