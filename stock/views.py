#!/usr/bin/env python3
#-*- coding:utf-8 -*-

from . import models
from . import serializers
from common.rest.viewsets import BaseViewSet,PermMethodViewSet
from rest_framework import viewsets,status,permissions
from rest_framework.response import Response

class WarehouseViewSet(BaseViewSet):
    model=models.Warehouse
    serializer_class = serializers.WarehouseSerializer

class ZoneViewSet(BaseViewSet):
    model=models.Zone
    serializer_class = serializers.ZoneSerializer

class LocationViewSet(BaseViewSet):
    model=models.Location
    serializer_class = serializers.LocationSerializer

class MoveViewSet(BaseViewSet):
    model=models.Move
    serializer_class = serializers.MoveSerializer

class PathViewSet(BaseViewSet):
    model=models.Path
    serializer_class = serializers.PathSerializer

class RouteViewSet(BaseViewSet):
    model=models.Route
    serializer_class = serializers.RouteSerializer

class RoutePathSortSettingViewSet(PermMethodViewSet):
    model=models.RoutePathSortSetting
    allow_actions = ('create','list','retrieve','update','destroy')

class PackageTypeProductSettingViewSet(PermMethodViewSet):
    model=models.PackageTypeProductSetting
    allow_actions = ('create','list','retrieve','update','destroy')
    serializer_class = serializers.PackageTypeProductSettingSerializer

class PackageTypeViewSet(BaseViewSet):
    model=models.PackageType
    serializer_class = serializers.PackageTypeSerializer

class PackageTemplateProductSettingViewSet(PermMethodViewSet):
    model = models.PackageTemplateProductSetting
    allow_actions = ('create', 'list', 'retrieve', 'update','destroy')
    serializer_class = serializers.PackageTypeProductSettingSerializer

class PackageTemplateViewSet(BaseViewSet):
    model=models.PackageTemplate
    serializer_class = serializers.PackageTemplateSerializer

class PackageNodeViewSet(BaseViewSet):
    model=models.PackageNode
    serializer_class = serializers.PackageNodeSerializer

class ProcurementFromLocationSettingViewSet(PermMethodViewSet):
    model = models.ProcurementFromLocationSetting
    allow_actions = ('create', 'list', 'retrieve', 'update','destroy')
    serializer_class = serializers.ProcurementFromLocationSettingSerializer

class ProcurementDetailViewSet(BaseViewSet):
    model=models.ProcurementDetail
    serializer_class = serializers.ProcurementDetailSerializer

class ProcurementViewSet(BaseViewSet):
    model=models.Procurement
    serializer_class = serializers.ProcurementSerializer

