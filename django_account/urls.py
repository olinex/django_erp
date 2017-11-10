#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r'user', views.UserViewSet, 'user')
router.register(r'profile', views.ProfileViewSet, 'profile')
router.register(r'partner', views.PartnerViewSet, 'partner')

urlpatterns = router.urls
