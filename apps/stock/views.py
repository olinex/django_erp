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

class ProcurementDetailViewSet(PermMethodViewSet):
    model = models.ProcurementDetail
    allow_actions = ('create', 'list', 'retrieve', 'update', 'destroy')
    serializer_class = serializers.ProcurementDetailSerializer


class ProcurementViewSet(BaseViewSet):
    model = models.Procurement
    serializer_class = serializers.ProcurementSerializer
