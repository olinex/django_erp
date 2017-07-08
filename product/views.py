#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from . import models
from . import serializers
from common.rest.viewsets import BaseViewSet, PermMethodViewSet
from rest_framework import viewsets, status, permissions
from rest_framework.response import Response


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
