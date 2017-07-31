#!/usr/bin/env python3
#-*- coding:utf-8 -*-

from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r'warehouse', views.WarehouseViewSet, 'warehouse')
router.register(r'zone', views.ZoneViewSet, 'zone')
router.register(r'location', views.LocationViewSet, 'location')
router.register(r'move', views.MoveViewSet, 'move')
router.register(r'route', views.RouteViewSet, 'route')
router.register(r'package-type/product-setting', views.PackageTypeProductSettingViewSet, 'package_type_product_setting')
router.register(r'package-type', views.PackageTypeViewSet, 'package_type')
router.register(r'package-template/product-setting', views.PackageTemplateProductSettingViewSet, 'package_template_product_setting')
router.register(r'package-template', views.PackageTemplateViewSet, 'package_template')
router.register(r'package-node', views.PackageNodeViewSet, 'package_node')
router.register(r'procurement/detail', views.ProcurementDetailViewSet, 'procurement_detail')
router.register(r'procurement', views.ProcurementViewSet, 'procurement')

urlpatterns = router.urls