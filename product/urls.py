#!/usr/bin/env python3
#-*- coding:utf-8 -*-

from . import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'category',views.ProductCategoryViewSet,'category')
router.register(r'attribute',views.AttributeViewSet,'attribute')
router.register(r'uom',views.UOMViewSet,'uom')
router.register(r'template',views.ProductTemplateViewSet,'template')
router.register(r'product',views.ProductViewSet,'product')

urlpatterns = router.urls