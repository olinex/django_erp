#!/usr/bin/env python3
# -*- coding:utf-8 -*-

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
from django.shortcuts import render
from django.conf.urls import include as origin_include
from django.utils.translation import ugettext_lazy as _
from rest_framework.documentation import include_docs_urls


def include(arg, namespace=None):
    if namespace not in settings.INSTALLED_APPS:
        raise ValueError(_('namespace {} must one of the app name in installed').format(namespace))
    return origin_include(arg=arg, namespace=namespace, app_name=namespace)


def first_request(request):
    return render(request, 'index.html')


urlpatterns = [
    url(r'^$', first_request, name='first_request'),
    url(r'^base/', include('django_base.urls', namespace='django_base')),
    url(r'^product/', include('django_product.urls', namespace='django_product')),
    # url(r'^stock/', include('django_stock.urls', namespace='django_stock')),
    # url(r'^test/', include('django_perm.urls', namespace='django_perm')),
    url(r'^admin/', admin.site.urls),
    url(r'^auth/', include('rest_framework.urls', namespace='rest_framework')),
]
if settings.SETUP_TOOLS:
    urlpatterns.append(url(r'^__debug__/', include(debug_toolbar.urls, namespace='debug_toolbar')))
    urlpatterns.append(url(r'^__document__/', include_docs_urls(title='document')))
if settings.FILE_SERVICE:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
