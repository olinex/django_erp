#!/usr/bin/env python3
#-*- coding:utf-8 -*-

from . import views
from rest_framework import routers
from django.views.decorators.csrf import csrf_protect

router = routers.DefaultRouter()
router.register(r'user',views.UserViewSet,'user')

urlpatterns = router.urls