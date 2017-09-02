#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from apps.account.models import Address
from apps.account.serializers import UserSerializer, AddressSerializer
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


class ZoneSerializer(ActiveModelSerializer):
    warehouse = StatePrimaryKeyRelatedField(models.Warehouse, 'active')
    warehouse_detail = WarehouseSerializer(source='warehouse', read_only=True)

    class Meta:
        model = models.Zone
        fields = ('warehouse', 'usage', 'warehouse_detail')


class LocationSerializer(ActiveModelSerializer):
    index = serializers.ReadOnlyField()
    zone_detail = ZoneSerializer(source='zone', read_only=True)

    class Meta:
        model = models.Location
        fields = (
            'zone', 'parent_node', 'is_virtual',
            'x', 'y', 'z', 'zone_detail', 'index'
        )


class RouteSettingSerializer(serializers.ModelSerializer):
    route = StatePrimaryKeyRelatedField(models.Route, 'active')
    location = StatePrimaryKeyRelatedField(models.Location, 'active')
    class Meta:
        model= models.RouteSetting
        fields=(
            'route','location','sequence'
        )

    def validate(self, data):
        route = data['route']
        location = data['location']
        if route.warehouse != location.zone.warehouse:
            raise serializers.ValidationError(_("the route's warehouse must equal to the location's warehouse"))
        return data


class RouteSerializer(ActiveModelSerializer):
    warehouse = StatePrimaryKeyRelatedField(models.Warehouse, 'active')
    warehouse_detail = WarehouseSerializer(source='warehouse', read_only=True)
    zones_detail = ZoneSerializer(source='zones',read_only=True,many=True)

    class Meta:
        model = models.Route
        fields = (
            'name', 'warehouse', 'warehouse_detail',
            'zones', 'zones_detail', 'sequence'
        )


class PackageTypeSettingSerializer(serializers.ModelSerializer):
    package_type = StatePrimaryKeyRelatedField(models.PackageType, 'active')
    item = StatePrimaryKeyRelatedField(models.Item, 'active')

    class Meta:
        model = models.PackageTypeSetting
        fields = (
            'package_type', 'item', 'max_quantity'
        )


class PackageTypeSerializer(ActiveModelSerializer):
    class Meta:
        model = models.PackageType
        fields = ('name', 'items')


class PackageTemplateSettingSerializer(serializers.ModelSerializer):
    package_template = StatePrimaryKeyRelatedField(models.PackageTemplate, 'active')
    type_setting_detail = PackageTypeSettingSerializer(
        source='type_setting',
        read_only=True,
        many=True
    )

    class Meta:
        model = models.PackageTemplateSetting
        fields = (
            'package_template', 'type_setting', 'quantity', 'type_setting_detail'
        )


class PackageTemplateSerializer(ActiveModelSerializer):
    package_type = StatePrimaryKeyRelatedField(models.PackageType, 'active')
    type_settings_detail = PackageTemplateSettingSerializer(
        source='type_settings',
        read_only=True,
        many=True
    )

    class Meta:
        model = models.PackageTemplate
        fields = (
            'name', 'package_type', 'type_settings', 'type_settings_detail'
        )


class PackageNodeSerializer(serializers.ModelSerializer):
    index = serializers.ReadOnlyField()
    template = StatePrimaryKeyRelatedField(models.PackageTemplate, 'active')
    template_detail = PackageTemplateSerializer(
        source='template',
        read_only=True
    )

    class Meta:
        model = models.PackageNode
        fields = (
            'name', 'parent_node', 'template', 'template_detail',
            'quantity', 'index'
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
    from_zone_detail = ZoneSerializer(source='from_zone', read_only=True)
    to_zone_detail = ZoneSerializer(source='to_zone', read_only=True)
    to_move = serializers.ReadOnlyField()
    procurement_detail_context = ProcurementDetailSerializer(source='procurement_detail',read_only=True)
    route_setting = serializers.ReadOnlyField()
    quantity = serializers.ReadOnlyField()
    state = serializers.CharField(read_only=True)

    class Meta:
        model = models.Move
        fields = (
            'from_zone_detail','to_zone_detail',
            'to_move', 'procurement_detail','procurement_detail_context',
            'route_setting', 'quantity', 'state'
        )
