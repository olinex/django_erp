#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
@author:    olinex
@time:      2017/9/26 下午1:30
"""

from rest_framework import routers
from . import views

router = routers.DefaultRouter()

router.register(r'province', views.ProvinceViewSet, 'province')
router.register(r'city', views.CityViewSet, 'city')
router.register(r'region', views.RegionViewSet, 'region')
router.register(r'address', views.AddressViewSet, 'address')
router.register(r'user', views.UserViewSet, 'user')
router.register(r'partner', views.PartnerViewSet, 'partner')

urlpatterns = router.urls
