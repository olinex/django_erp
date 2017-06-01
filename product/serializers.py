#!/usr/bin/env python3
#-*- coding:utf-8 -*-

import json
from . import models
from django.db import transaction
from rest_framework import serializers
from common.rest.serializers import ActiveModelSerializer

class ProductCategorySerializer(ActiveModelSerializer):
    class Meta:
        model=models.ProductCategory
        fields=('name','sequence')

class AttributeSerializer(ActiveModelSerializer):
    value=serializers.ListField(child=serializers.CharField(max_length=190))
    class Meta:
        model=models.Attribute
        fields=('id','name','value')

class UOMSerializer(ActiveModelSerializer):
    class Meta:
        model=models.UOM
        fields=(
            'name','symbol','decimal_places',
            'round_method','ratio_type',
            'ratio','category'
        )

class ProductTemplateSerializer(ActiveModelSerializer):
    uom_detail=UOMSerializer(
        source='uom',
        read_only=True
    )
    attributes_detail=AttributeSerializer(
        source='attributes',
        read_only=True,
        many=True
    )
    class Meta:
        model=models.ProductTemplate
        fields=(
            'id','name','attributes',
            'uom','sequence','detail',
            'in_description','out_description',
            'category','uom_detail','attributes_detail'
        )

class ProductSerializer(ActiveModelSerializer):
    template_detail=ProductTemplateSerializer(
        source='template',
        read_only=True
    )
    attributes=serializers.DictField(child=serializers.CharField(max_length=190))
    class Meta:
        model=models.Product
        fields=(
            'id','template','attributes',
            'in_code','out_code','weight',
            'volume','salable','purchasable',
            'rentable','template_detail'
        )


