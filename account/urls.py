#!/usr/bin/env python3
#-*- coding:utf-8 -*-

from . import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'user',views.UserViewSet,'user')
router.register(r'province',views.ProvinceViewSet,'province')
router.register(r'city',views.CityViewSet,'city')
router.register(r'region',views.RegionViewSet,'region')
router.register(r'address',views.AddressViewSet,'address')
router.register(r'company',views.CompanyViewSet,'company')

urlpatterns = router.urls