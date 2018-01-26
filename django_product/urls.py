#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r'attribute', views.AttributeViewSet, 'attribute')

urlpatterns = router.urls