#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from . import models
from . import serializers
from common.rest.viewsets import BaseViewSet, PermMethodViewSet
from rest_framework import viewsets, status, permissions
from rest_framework.response import Response


class WarehouseViewSet(BaseViewSet):
    model = models.Warehouse
    serializer_class = serializers.WarehouseSerializer


class ZoneViewSet(BaseViewSet):
    model = models.Zone
    serializer_class = serializers.ZoneSerializer


class LocationViewSet(BaseViewSet):
    model = models.Location
    serializer_class = serializers.LocationSerializer


class MoveViewSet(BaseViewSet):
    model = models.Move
    allow_actions = ('list', 'retrieve')
    serializer_class = serializers.MoveSerializer


class RouteViewSet(BaseViewSet):
    model = models.Route
    serializer_class = serializers.RouteSerializer

class RouteSettingViewSet(PermMethodViewSet):
    model = models.RouteSetting
    allow_actions = ('create', 'list', 'retrieve', 'update', 'destroy')
    serializer_class = serializers.RouteSettingSerializer


class PackageTypeSettingViewSet(PermMethodViewSet):
    model = models.PackageTypeSetting
    allow_actions = ('create', 'list', 'retrieve', 'update', 'destroy')
    serializer_class = serializers.PackageTypeSettingSerializer


class PackageTypeViewSet(BaseViewSet):
    model = models.PackageType
    serializer_class = serializers.PackageTypeSerializer


class PackageTemplateSettingViewSet(PermMethodViewSet):
    model = models.PackageTemplateSetting
    allow_actions = ('create', 'list', 'retrieve', 'update', 'destroy')
    serializer_class = serializers.PackageTemplateSettingSerializer


class PackageTemplateViewSet(BaseViewSet):
    model = models.PackageTemplate
    serializer_class = serializers.PackageTemplateSerializer


class PackageNodeViewSet(PermMethodViewSet):
    model = models.PackageNode
    allow_actions = ('create', 'list', 'retrieve', 'update', 'destroy')
    serializer_class = serializers.PackageNodeSerializer


class ProcurementDetailViewSet(PermMethodViewSet):
    model = models.ProcurementDetail
    allow_actions = ('create', 'list', 'retrieve', 'update', 'destroy')
    serializer_class = serializers.ProcurementDetailSerializer


class ProcurementViewSet(BaseViewSet):
    model = models.Procurement
    serializer_class = serializers.ProcurementSerializer
