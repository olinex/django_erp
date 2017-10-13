#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from django_base.models import Address
from django_base.serializers import AddressSerializer
from django_account.serializers import UserSerializer
from common.rest.serializers import ActiveModelSerializer, StatePrimaryKeyRelatedField
from . import models

User = get_user_model()


class WarehouseSerializer(ActiveModelSerializer):
    user_detail = UserSerializer(source='user', read_only=True)
    address_detail = AddressSerializer(source='address', read_only=True)
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(is_active=True)
    )
    address = StatePrimaryKeyRelatedField(Address, 'active')

    class Meta:
        model = models.Warehouse
        fields = ('name', 'user', 'address', 'user_detail', 'address_detail')


class LocationSerializer(ActiveModelSerializer):
    index = serializers.ReadOnlyField()
    warehouse_detail = WarehouseSerializer(source='warehouse', read_only=True)

    class Meta:
        model = models.Location
        fields = (
            'warehouse', 'parent_node', 'is_virtual',
            'x', 'y', 'z', 'warehouse_detail', 'index'
        )


class RouteSettingSerializer(serializers.ModelSerializer):
    route = StatePrimaryKeyRelatedField(models.Route, 'active')
    location = StatePrimaryKeyRelatedField(models.Location, 'active')

    class Meta:
        model = models.RouteSetting
        fields = (
            'route', 'location', 'sequence'
        )

    def validate(self, data):
        route = data['route']
        location = data['location']
        if route.warehouse != location.warehouse:
            raise serializers.ValidationError(_("the route's warehouse must equal to the location's warehouse"))
        return data


class RouteSerializer(ActiveModelSerializer):
    warehouse = StatePrimaryKeyRelatedField(models.Warehouse, 'active')
    warehouse_detail = WarehouseSerializer(source='warehouse', read_only=True)
    locations_detail = LocationSerializer(source='locations', read_only=True, many=True)

    class Meta:
        model = models.Route
        fields = (
            'name', 'warehouse', 'warehouse_detail',
            'locations', 'locations_detail', 'sequence'
        )


class ProcurementDetailSerializer(ActiveModelSerializer):
    from_location_detail = LocationSerializer(source='from_location', read_only=True)
    next_location_detail = LocationSerializer(source='next_location', read_only=True)
    item = StatePrimaryKeyRelatedField(models.Item, 'active')

    class Meta:
        model = models.ProcurementDetail
        fields = (
            'from_location', 'next_location', 'direct_return',
            'from_location_detail', 'next_location_detail',
            'item', 'quantity', 'procurement'
        )


class ProcurementSerializer(ActiveModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(is_active=True)
    )
    user_detail = UserSerializer(source='user', read_only=True)
    route = StatePrimaryKeyRelatedField(models.Route, 'active')
    route_detail = RouteSerializer(source='route', read_only=True)

    class Meta:
        model = models.Procurement
        fields = (
            'user', 'user_detail', 'state', 'route', 'route_detail'
        )


class MoveSerializer(ActiveModelSerializer):
    from_location_detail = LocationSerializer(source='from_location', read_only=True)
    to_location_detail = LocationSerializer(source='to_location', read_only=True)
    to_move = serializers.ReadOnlyField()
    procurement_detail_context = ProcurementDetailSerializer(source='procurement_detail', read_only=True)
    from_route_setting = serializers.ReadOnlyField()
    to_route_setting = serializers.ReadOnlyField()
    quantity = serializers.ReadOnlyField()
    state = serializers.CharField(read_only=True)

    class Meta:
        model = models.Move
        fields = (
            'from_location_detail', 'to_location_detail',
            'to_move', 'procurement_detail', 'procurement_detail_context',
            'from_route_setting', 'to_route_setting', 'quantity', 'state'
        )
