#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from rest_framework import serializers

from common.rest.serializers import ActiveModelSerializer, StatePrimaryKeyRelatedField
from . import models

class ItemSerializer(ActiveModelSerializer):
    class Meta:
        model = models.Item
        fields = ('content_type', 'object_id')


class ProductCategorySerializer(ActiveModelSerializer):
    class Meta:
        model = models.ProductCategory
        fields = ('name', 'sequence')


class AttributeSerializer(ActiveModelSerializer):
    value = serializers.ListField(child=serializers.CharField(max_length=190))
    extra_price = serializers.ListField(child=serializers.CharField(max_length=190))

    class Meta:
        model = models.Attribute
        fields = ('id', 'name', 'value', 'extra_price')


class UOMSerializer(ActiveModelSerializer):
    class Meta:
        model = models.UOM
        fields = (
            'id', 'name', 'symbol', 'decimal_places',
            'round_method', 'ratio', 'category'
        )


class ValidateActionSerializer(ActiveModelSerializer):
    symbol = serializers.ReadOnlyField()
    uom = serializers.ReadOnlyField()

    class Meta:
        model = models.ValidateAction
        fields = ('symbol', 'name', 'uom', 'explain')


class ValidationSerializer(ActiveModelSerializer):
    actions = StatePrimaryKeyRelatedField(models.ValidateAction, 'active', many=True)
    actions_detail = ValidateActionSerializer(source='actions', read_only=True, many=True)

    class Meta:
        model = models.Validation
        fields = ('name', 'actions', 'actions_detail')


class ProductTemplateSerializer(ActiveModelSerializer):
    uom_detail = UOMSerializer(
        source='uom',
        read_only=True
    )
    attributes_detail = AttributeSerializer(
        source='attributes',
        read_only=True,
        many=True
    )
    uom = StatePrimaryKeyRelatedField(models.UOM, 'active')
    attributes = StatePrimaryKeyRelatedField(models.Attribute, 'active', many=True)
    category = StatePrimaryKeyRelatedField(models.ProductCategory, 'active')
    validation = StatePrimaryKeyRelatedField(models.Validation, 'active')
    validation_detail = ValidationSerializer(source='validation', read_only=True)

    class Meta:
        model = models.ProductTemplate
        fields = (
            'id', 'name', 'attributes', 'stock_type',
            'uom', 'sequence', 'detail',
            'in_description', 'out_description',
            'validation', 'validation_detail',
            'category', 'uom_detail', 'attributes_detail'
        )


class ProductSerializer(ActiveModelSerializer):
    template_detail = ProductTemplateSerializer(
        source='template',
        read_only=True
    )
    attributes = serializers.DictField(child=serializers.CharField(max_length=190), read_only=True)
    prices = serializers.DictField(child=serializers.CharField(max_length=190), read_only=True)
    template = StatePrimaryKeyRelatedField(models.ProductTemplate, 'active')

    class Meta:
        model = models.Product
        fields = (
            'id', 'template', 'attributes', 'prices',
            'in_code', 'out_code', 'weight',
            'volume', 'salable', 'purchasable',
            'rentable', 'template_detail'
        )


class LotSerializer(ActiveModelSerializer):
    product = StatePrimaryKeyRelatedField(models.Product, 'active')

    class Meta:
        model = models.Lot
        fields = ('name', 'product')

class PackageTypeSettingSerializer(serializers.ModelSerializer):
    package_type = StatePrimaryKeyRelatedField(models.PackageType, 'active')
    item = StatePrimaryKeyRelatedField(models.Item, 'active')
    item_detail = ItemSerializer(source='item', read_only=True)

    class Meta:
        model = models.PackageTypeSetting
        fields = (
            'package_type', 'item', 'item_detail', 'max_quantity'
        )


class PackageTypeSerializer(ActiveModelSerializer):
    item_settings = PackageTypeSettingSerializer(
        source='packagetypesetting_set',
        read_only=True,
        many=True
    )

    class Meta:
        model = models.PackageType
        fields = ('name', 'item_settings')


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
    item_settings = PackageTemplateSettingSerializer(
        source='packagetemplatesetting_set',
        read_only=True,
        many=True
    )

    class Meta:
        model = models.PackageTemplate
        fields = (
            'name', 'package_type', 'item_settings'
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
