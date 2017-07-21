#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from . import models
from product.models import Product,Lot
from account.models import Address
from rest_framework import serializers
from common.rest.serializers import ActiveModelSerializer,StatePrimaryKeyRelatedField
from account.serializers import UserSerializer, AddressSerializer
from product.serializers import ProductSerializer,LotSerializer
from django.contrib.auth import get_user_model

User = get_user_model()


class WarehouseSerializer(ActiveModelSerializer):
    user_detail = UserSerializer(source='user', read_only=True)
    address_detail = AddressSerializer(source='address', read_only=True)
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(is_active=True,profile__is_partner=True)
    )
    address = StatePrimaryKeyRelatedField(Address,'active')

    class Meta:
        model = models.Warehouse
        fields = ('name', 'user', 'address', 'user_detail', 'address_detail')


class ZoneSerializer(ActiveModelSerializer):
    warehouse = StatePrimaryKeyRelatedField(models.Warehouse,'active')
    warehouse_detail = WarehouseSerializer(source='warehouse', read_only=True)

    class Meta:
        model = models.Zone
        fields = ('warehouse', 'usage', 'warehouse_detail')


class LocationSerializer(ActiveModelSerializer):
    level=serializers.ReadOnlyField()
    index=serializers.ReadOnlyField()
    zone_detail = ZoneSerializer(source='zone', read_only=True)

    class Meta:
        model = models.Location
        fields = (
            'zone', 'parent_node', 'is_virtual',
            'x', 'y', 'z', 'zone_detail','level','index'
        )


class MoveSerializer(ActiveModelSerializer):
    initial_location_detail = LocationSerializer(source='initial_location', read_only=True)
    end_location_detail = LocationSerializer(source='end_location', read_only=True)
    from_location_detail = LocationSerializer(source='from_location', read_only=True)
    to_location_detail = LocationSerializer(source='to_location', read_only=True)
    to_move = serializers.ReadOnlyField()
    procurement_detail_setting = serializers.ReadOnlyField()
    route_path_sort_setting = serializers.ReadOnlyField()
    quantity = serializers.ReadOnlyField()
    state = serializers.CharField(read_only=True)

    class Meta:
        model = models.Move
        fields = (
            'initial_location_detail',
            'end_location_detail',
            'from_location_detail',
            'to_location_detail',
            'to_move', 'procurement_detail_setting',
            'route_path_sort_setting','quantity', 'state'
        )


class PathSerializer(ActiveModelSerializer):
    from_location = StatePrimaryKeyRelatedField(models.Location,'active')
    to_location = StatePrimaryKeyRelatedField(models.Location,'active')
    from_location_detail = LocationSerializer(source='from_location', read_only=True)
    to_location_detail = LocationSerializer(source='to_location', read_only=True)

    class Meta:
        model = models.Path
        fields = (
            'from_location', 'from_location_detail',
            'to_location', 'to_location_detail',
        )

class RouteSerializer(ActiveModelSerializer):
    warehouse = StatePrimaryKeyRelatedField(models.Warehouse,'active')
    warehouse_detail=WarehouseSerializer(source='warehouse',read_only=True)
    paths_detail=PathSerializer(source='paths',many=True,read_only=True)
    class Meta:
        model=models.Route
        fields=(
            'name','warehouse','warehouse_detail',
            'direct_path','paths_detail','return_route',
            'return_method','sequence'
        )

class RoutePathSortSettingSerializer(serializers.ModelSerializer):
    route = StatePrimaryKeyRelatedField(models.Route,'active')
    path = StatePrimaryKeyRelatedField(models.Path,'active')
    class Meta:
        model=models.RoutePathSortSetting
        fields=(
            'route','path','sequence'
        )

class PackageTypeProductSettingSerializer(serializers.ModelSerializer):
    package_type = StatePrimaryKeyRelatedField(models.PackageType,'active')
    product = StatePrimaryKeyRelatedField(Product,'active')
    product_detail=ProductSerializer(source='product',read_only=True)
    class Meta:
        model=models.PackageTypeProductSetting
        fields=(
            'package_type','product','product_detail','max_quantity'
        )

class PackageTypeSerializer(ActiveModelSerializer):
    products_detail=PackageTypeProductSettingSerializer(
        source='products',
        read_only=True,
        many=True
    )
    class Meta:
        model=models.PackageType
        fields=('name','products_detail')

class PackageTemplateProductSettingSerializer(serializers.ModelSerializer):
    package_template = StatePrimaryKeyRelatedField(models.PackageTemplate,'active')
    product = StatePrimaryKeyRelatedField(Product,'active')
    class Meta:
        model=models.PackageTypeProductSetting
        fields=(
            'package_template','product','quantity'
        )

class PackageTemplateSerializer(ActiveModelSerializer):
    package_type = StatePrimaryKeyRelatedField(models.PackageType,'active')
    products_detail=PackageTemplateProductSettingSerializer(
        source='products',
        read_only=True,
        many=True
    )
    package_type_detail=PackageTypeSerializer(
        source='package_type',
        read_only=True,
    many=True
    )
    class Meta:
        model=models.PackageTemplate
        fields=(
            'name','package_type','products_detail'
        )

class PackageNodeSerializer(serializers.ModelSerializer):
    level=serializers.ReadOnlyField()
    index=serializers.ReadOnlyField()
    template = StatePrimaryKeyRelatedField(models.PackageTemplate,'active')
    template_detail=PackageTemplateSerializer(
        source='template',
        read_only=True
    )
    class Meta:
        model=models.PackageNode
        fields=(
            'name','parent_node','template','template_detail',
            'quantity','level','index'
        )

class ProcurementFromLocationSettingSerializer(serializers.ModelSerializer):
    detail = StatePrimaryKeyRelatedField(models.ProcurementDetail,'active')
    location = StatePrimaryKeyRelatedField(models.Location,'active')
    route = StatePrimaryKeyRelatedField(models.Route,'active')
    location_detail=LocationSerializer(source='location',read_only=True)
    route_detail=RouteSerializer(source='route',read_only=True)
    class Meta:
        model=models.ProcurementFromLocationSetting
        fields=(
            'detail','location','location_detail','quantity',
            'route','route_detail'
        )

class ProcurementDetailSerializer(ActiveModelSerializer):
    from_location = StatePrimaryKeyRelatedField(models.Location,'active')
    from_locations_detail=ProcurementFromLocationSettingSerializer(
        source='from_location',
        read_only=True,
        many=True
    )
    product = StatePrimaryKeyRelatedField(Product,'active')
    product_detail=ProductSerializer(source='product',read_only=True)
    lot = StatePrimaryKeyRelatedField(Lot,'active')
    lot_detail=LotSerializer(source='lot',read_only=True)
    class Meta:
        model=models.ProcurementDetail
        fields=(
            'from_location','from_location_detail',
            'product','product_detail',
            'lot','lot_detail','procurement'
        )

class ProcurementSerializer(ActiveModelSerializer):
    to_location = StatePrimaryKeyRelatedField(models.Location,'active')
    to_location_detail=LocationSerializer(source='to_location',read_only=True)
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(is_active=True,profile__is_partner=True)
    )
    user_detail=UserSerializer(source='user',read_only=True)
    class Meta:
        model=models.Procurement
        fields=(
            'to_location','to_location_detail',
            'user','user_detail','state'
        )