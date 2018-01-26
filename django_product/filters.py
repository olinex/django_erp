#!/usr/bin/env python3
# -*- coding:utf-8 -*-

__all__ = ['AttributeFilter']

from . import models
from django_erp.common import filters
from django.contrib.auth import get_user_model

User = get_user_model()


class AttributeFilter(filters.FilterSet):
    ordering = filters.OrderingFilter(
        fields=(
            ('id', 'id'),
            ('name', 'name'),
            ('sequence', 'sequence')
        )
    )

    class Meta:
        model = models.Attribute
        fields = {
            'name': filters.CHAR_FILTER_TYPE,
        }
        fields.update(filters.sequence_model_fields)


class LotFilter(filters.FilterSet):
    ordering = filters.OrderingFilter(
        fields=(
            ('id', 'id'),
            ('name', 'name'),
            ('product__id', 'product'),
            ('product__template__name', 'product__template__name'),
            ('sequence', 'sequence')
        )
    )

    class Meta:
        model = models.Lot
        fields = {
            'name': filters.CHAR_FILTER_TYPE,
            'product': filters.NUMBER_FILTER_TYPE,
            'product__template__name': filters.NUMBER_FILTER_TYPE,
        }
        fields.update(filters.sequence_model_fields)


# class ProductFilter(filters.FilterSet):
#     ordering = filters.OrderingFilter(
#         fields=(
#             ('id', 'id'),
#             ('template__id', 'template'),
#             ('template__name', 'template__name'),
#             ('template__stock_type', 'template__stock_type'),
#             ('template__uom__id', 'template__uom__id'),
#             ('product__id', 'product'),
#             ('product__name', 'product__name'),
#             ('sequence', 'sequence')
#         )
#     )
#
#     class Meta:
#         model = models.Product
#         fields = {
#             'name': filters.CHAR_FILTER_TYPE,
#             'product': filters.NUMBER_FILTER_TYPE,
#             'product__name': filters.NUMBER_FILTER_TYPE,
#         }
#         fields.update(filters.sequence_model_fields)