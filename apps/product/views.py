#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from common.rest.viewsets import BaseViewSet, PermMethodViewSet
from . import models
from . import serializers


class ProductCategoryViewSet(BaseViewSet):
    model = models.ProductCategory
    serializer_class = serializers.ProductCategorySerializer


class AttributeViewSet(BaseViewSet):
    model = models.Attribute
    serializer_class = serializers.AttributeSerializer


class UOMViewSet(BaseViewSet):
    model = models.UOM
    serializer_class = serializers.UOMSerializer


class ProductTemplateViewSet(BaseViewSet):
    model = models.ProductTemplate
    serializer_class = serializers.ProductTemplateSerializer


class ProductViewSet(BaseViewSet):
    model = models.Product
    serializer_class = serializers.ProductSerializer


class LotViewSet(BaseViewSet):
    model = models.Lot
    serializer_class = serializers.LotSerializer


class ValidateActionViewSet(BaseViewSet):
    model = models.ValidateAction
    serializer_class = serializers.ValidateActionSerializer


class ValidationViewSet(BaseViewSet):
    model = models.Validation
    serializer_class = serializers.ValidationSerializer

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

class ItemViewSet(BaseViewSet):
    model = models.Item
    serializer_class = serializers.ItemSerializer

