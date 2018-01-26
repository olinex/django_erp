#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
@author:    olinex
@time:      2017/9/26 下午1:30
"""

from rest_framework import routers
from . import views

router = routers.DefaultRouter()

router.register(r'argument', views.ArgumentViewSet, 'argument')
router.register(r'city', views.CityViewSet, 'city')
router.register(r'content_type', views.ContentTypeViewSet, 'content_type')
router.register(r'email_account', views.EmailAccountViewSet, 'email_account')
router.register(r'group', views.GroupViewSet, 'group')
router.register(r'permission', views.PermissionViewSet, 'permission')
router.register(r'message', views.MessageViewSet, 'message')
router.register(r'partner', views.PartnerViewSet, 'partner')
router.register(r'province', views.ProvinceViewSet, 'province')
router.register(r'region', views.RegionViewSet, 'region')
router.register(r'user', views.UserViewSet, 'user')
router.register(r'change', views.ChangeViewSet, 'change')
router.register(r'redis', views.RedisViewSet, 'redis')

urlpatterns = router.urls
