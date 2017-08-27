#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from rest_framework import serializers

from common.rest.serializers import ActiveModelSerializer, StatePrimaryKeyRelatedField
from . import models


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
            'name', 'symbol', 'decimal_places',
            'round_method', 'ratio', 'category'
        )


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

    class Meta:
        model = models.ProductTemplate
        fields = (
            'id', 'name', 'attributes',
            'uom', 'sequence', 'detail',
            'in_description', 'out_description',
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


class ValidateActionSerializer(ActiveModelSerializer):
    symbol = serializers.ReadOnlyField()
    uom = serializers.ReadOnlyField()

    class Meta:
        model = models.ValidateAction
        fields = ('symbol','name', 'uom', 'explain')


class ValidationSerializer(ActiveModelSerializer):
    actions = StatePrimaryKeyRelatedField(models.ValidateAction, 'active', many=True)
    actions_detail = ValidateActionSerializer(source='actions', read_only=True, many=True)

    class Meta:
        model = models.Validation
        fields = ('name', 'actions','actions_detail')
