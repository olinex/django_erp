"""djangoerp URL Configuration

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
from django.conf.urls import url,include
from django.contrib import admin
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static
from account.views import first_request

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^auth/',include('rest_framework.urls',namespace='rest_framework',app_name='rest_framework')),
    url(r'^account/',include('account.urls',namespace='account',app_name='account')),
    url(r'^product/',include('product.urls',namespace='product',app_name='product')),
    url(r'^stock/',include('stock.urls',namespace='stock',app_name='stock')),
    url(r'^test/',include('djangoperm.urls',namespace='djangoperm',app_name='djangoperm')),
    url(r'^$', first_request, name='first_request'),
]

urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.STATIC_URL,document_root=settings.STATIC_ROOT)


