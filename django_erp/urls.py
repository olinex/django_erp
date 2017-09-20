"""django_erp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
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
import debug_toolbar
from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin
from django_account.views import first_request
from common.utils import include

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^auth/',include('rest_framework.urls',namespace='rest_framework')),
    url(r'^account/', include('django_account.urls', namespace='django_account')),
    url(r'^product/', include('django_product.urls', namespace='django_product')),
    url(r'^stock/', include('django_stock.urls', namespace='django_stock')),
    url(r'^test/', include('django_perm.urls', namespace='django_perm')),

    url(r'^__debug__/',include(debug_toolbar.urls,namespace='debug')),
    url(r'^$', first_request, name='first_request'),
]
if settings.FILE_SERVICE:
    urlpatterns += static(settings.STATIC_URL,document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)


