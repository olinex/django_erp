#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from django.contrib.auth import get_user_model
from apps.product.models import Product, Lot, ProductCategory
from rest_framework import serializers

from apps.account.models import Address
from apps.account.serializers import UserSerializer, AddressSerializer
from apps.product.serializers import ProductSerializer, LotSerializer, ProductCategorySerializer
from common.rest.serializers import ActiveModelSerializer, StatePrimaryKeyRelatedField
from . import models

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
    warehouse = StatePrimaryKeyRelatedField(models.Warehouse, 'active')
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
    from_zone_detail = ZoneSerializer(source='from_zone', read_only=True)
    to_zone_detail = ZoneSerializer(source='to_zone', read_only=True)
    to_move = serializers.ReadOnlyField()
    procurement_detail = serializers.ReadOnlyField()
    route_zone_setting = serializers.ReadOnlyField()
    quantity = serializers.ReadOnlyField()
    state = serializers.CharField(read_only=True)

    class Meta:
        model = models.Move
        fields = (
            'from_zone_detail',
            'to_zone_detail',
            'to_move', 'procurement_detail',
            'route_zone_setting','quantity', 'state'
        )


class RouteSerializer(ActiveModelSerializer):
    warehouse = StatePrimaryKeyRelatedField(models.Warehouse, 'active')
    warehouse_detail=WarehouseSerializer(source='warehouse',read_only=True)
    zones_detail=ZoneSerializer(source='zones',many=True,read_only=True)
    class Meta:
        model= models.Route
        fields=(
            'name','warehouse','warehouse_detail',
            'zones_detail','sequence'
        )

class RouteZoneSettingSerializer(serializers.ModelSerializer):
    route = StatePrimaryKeyRelatedField(models.Route, 'active')
    zone = StatePrimaryKeyRelatedField(models.Zone, 'active')
    class Meta:
        model= models.RouteZoneSetting
        fields=(
            'route','zone','sequence'
        )

    def validate(self, attrs):
        route = attrs['route']
        zone = attrs['zone']
        if route.warehouse != zone.warehouse:
            raise serializers.ValidationError('区域所属的仓库必须与路线的仓库相同')
        return attrs

class PackageTypeCategorySettingSerializer(serializers.ModelSerializer):
    package_type = StatePrimaryKeyRelatedField(models.PackageType, 'active')
    product_category = StatePrimaryKeyRelatedField(ProductCategory,'active')
    product_category_detail=ProductCategorySerializer(source='product_category',read_only=True)
    class Meta:
        model= models.PackageTypeCategorySetting
        fields=(
            'package_type','product_category','product_category_detail','max_quantity'
        )

class PackageTypeSerializer(ActiveModelSerializer):
    categories_detail=PackageTypeCategorySettingSerializer(
        source='categories',
        read_only=True,
        many=True
    )
    class Meta:
        model= models.PackageType
        fields=('name','categories_detail')

class PackageTemplateCategorySettingSerializer(serializers.ModelSerializer):
    package_template = StatePrimaryKeyRelatedField(models.PackageTemplate, 'active')
    type_setting_detail = PackageTypeCategorySettingSerializer(
        source='type_setting',
        read_only=True,
        many=True
    )
    class Meta:
        model= models.PackageTemplateCategorySetting
        fields=(
            'package_template','type_setting','quantity','type_setting_detail'
        )

class PackageTemplateSerializer(ActiveModelSerializer):
    package_type = StatePrimaryKeyRelatedField(models.PackageType, 'active')
    type_settings_detail=PackageTemplateCategorySettingSerializer(
        source='type_settings',
        read_only=True,
        many=True
    )
    class Meta:
        model= models.PackageTemplate
        fields=(
            'name','package_type','type_settings','type_settings_detail'
        )

class PackageNodeSerializer(serializers.ModelSerializer):
    level=serializers.ReadOnlyField()
    index=serializers.ReadOnlyField()
    template = StatePrimaryKeyRelatedField(models.PackageTemplate, 'active')
    template_detail=PackageTemplateSerializer(
        source='template',
        read_only=True
    )
    class Meta:
        model= models.PackageNode
        fields=(
            'name','parent_node','template','template_detail',
            'quantity','level','index'
        )

class ProcurementDetailSerializer(ActiveModelSerializer):
    product = StatePrimaryKeyRelatedField(Product,'active')
    product_detail=ProductSerializer(source='product',read_only=True)
    lot = StatePrimaryKeyRelatedField(Lot,'active')
    lot_detail=LotSerializer(source='lot',read_only=True)
    class Meta:
        model= models.ProcurementDetail
        fields=(
            'product','product_detail','quantity',
            'lot','lot_detail','procurement'
        )


class ProcurementSerializer(ActiveModelSerializer):
    to_location = StatePrimaryKeyRelatedField(models.Location, 'active')
    to_location_detail=LocationSerializer(source='to_location',read_only=True)
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(is_active=True,profile__is_partner=True)
    )
    user_detail=UserSerializer(source='user',read_only=True)
    route = StatePrimaryKeyRelatedField(models.Route, 'active')
    route_detail = RouteSerializer(source='route',read_only=True)
    class Meta:
        model= models.Procurement
        fields=(
            'to_location','to_location_detail',
            'user','user_detail','state','route','route_detail'
        )