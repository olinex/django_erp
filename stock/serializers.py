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
    route_path_setting = serializers.ReadOnlyField()
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
            'route_path_setting','quantity', 'state'
        )


class RouteSerializer(ActiveModelSerializer):
    warehouse = StatePrimaryKeyRelatedField(models.Warehouse,'active')
    warehouse_detail=WarehouseSerializer(source='warehouse',read_only=True)
    locations_detail=LocationSerializer(source='locations',many=True,read_only=True)
    class Meta:
        model=models.Route
        fields=(
            'name','warehouse','warehouse_detail',
            'locations_detail','return_route',
            'return_method','sequence'
        )

class RouteLocationSettingSerializer(serializers.ModelSerializer):
    route = StatePrimaryKeyRelatedField(models.Route,'active')
    location = StatePrimaryKeyRelatedField(models.Location,'active')
    class Meta:
        model=models.RouteLocationSetting
        fields=(
            'route','location','sequence'
        )

    def validate(self, attrs):
        route = attrs['route']
        path = attrs['location']
        if (route.warehouse != path.from_location.zone.warehouse or
            route.warehouse != path.to_location.zone.warehouse):
            raise serializers.ValidationError('路径所属的仓库必须与路线的仓库相同')
        return attrs

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

class ProcurementDetailSerializer(ActiveModelSerializer):
    product = StatePrimaryKeyRelatedField(Product,'active')
    product_detail=ProductSerializer(source='product',read_only=True)
    lot = StatePrimaryKeyRelatedField(Lot,'active')
    lot_detail=LotSerializer(source='lot',read_only=True)
    route = StatePrimaryKeyRelatedField(models.Route,'active')
    route_detail = RouteSerializer(source='route',read_only=True)
    class Meta:
        model=models.ProcurementDetail
        fields=(
            'product','product_detail',
            'route','route_detail',
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