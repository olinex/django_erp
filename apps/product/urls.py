#!/usr/bin/env python3
#-*- coding:utf-8 -*-

from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r'category', views.ProductCategoryViewSet, 'category')
router.register(r'attribute', views.AttributeViewSet, 'attribute')
router.register(r'uom', views.UOMViewSet, 'uom')
router.register(r'template', views.ProductTemplateViewSet, 'template')
router.register(r'product', views.ProductViewSet, 'product')
router.register(r'lot', views.LotViewSet, 'lot')
router.register(r'validate-action', views.ValidateActionViewSet, 'validate_action')
router.register(r'validation', views.ValidationViewSet, 'validation')

urlpatterns = router.urls