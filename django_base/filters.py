#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
@author:    olinex
@time:      2017/9/30 上午1:25
"""

__all__ = [
    'UserFilter',
    'PermissionFilter',
    'ProvinceFilter',
    'CityFilter',
    'RegionFilter',
    'AddressFilter',
    'ArgumentFilter',
    'GroupFilter',
    'MessageFilter',
    'PartnerFilter',

]

from . import models
from django_erp.common import filters
from django.contrib.auth import get_user_model
from django.contrib.auth.models import ContentType, Group, Permission

User = get_user_model()


class ProvinceFilter(filters.FilterSet):
    ordering = filters.OrderingFilter(
        fields=(
            ('id', 'id'),
            ('country', 'country'),
            ('name', 'name')
        )
    )

    class Meta:
        model = models.Province
        fields = {
            'name':filters.CHAR_FILTER_TYPE,
            'country': filters.CHAR_FILTER_TYPE
        }
        fields.update(filters.data_model_fields)


class CityFilter(filters.FilterSet):
    ordering = filters.OrderingFilter(
        fields=(
            ('id', 'id'),
            ('province__id', 'province'),
            ('province__name', 'province__name'),
            ('province__country', 'province__country'),
            ('name', 'name')
        )
    )

    class Meta:
        model = models.City
        fields = {
            'name': filters.CHAR_FILTER_TYPE,
            'province': filters.NUMBER_FILTER_TYPE,
            'province__name': filters.CHAR_FILTER_TYPE,
            'province__country': filters.CHAR_FILTER_TYPE,
        }
        fields.update(filters.data_model_fields)


class RegionFilter(filters.FilterSet):
    ordering = filters.OrderingFilter(
        fields=(
            ('id', 'id'),
            ('city__provine__name', 'city__provine__name'),
            ('city__provine__country', 'city__provine__country'),
            ('city__provine__id', 'city__province'),
            ('city__id', 'city'),
            ('city__name', 'city__name'),
            ('name', 'name')
        )
    )

    class Meta:
        model = models.Region
        fields = {
            'name': filters.CHAR_FILTER_TYPE,
            'city__province': filters.NUMBER_FILTER_TYPE,
            'city__province__country': filters.NUMBER_FILTER_TYPE,
            'city__province__name': filters.CHAR_FILTER_TYPE,
            'city': filters.NUMBER_FILTER_TYPE,
            'city__name': filters.CHAR_FILTER_TYPE
        }
        fields.update(filters.data_model_fields)


class AddressFilter(filters.FilterSet):
    ordering = filters.OrderingFilter(
        fields=(
            ('id', 'id'),
            ('region__id', 'region'),
            ('name', 'name')
        )
    )

    class Meta:
        model = models.Address
        fields = {
            'id': filters.NUMBER_FILTER_TYPE,
            'name': filters.CHAR_FILTER_TYPE
        }


class ArgumentFilter(filters.FilterSet):
    ordering = filters.OrderingFilter(
        fields=(
            ('id', 'id'),
            ('name', 'name'),
            ('form', 'form'),
            ('value', 'value')
        )
    )

    class Meta:
        model = models.Argument
        fields = {
            'name': filters.CHAR_FILTER_TYPE,
            'form': filters.CHOICE_FILTER_TYPE,
            'value': filters.CHAR_FILTER_TYPE
        }


class ContentTypeFilter(filters.FilterSet):
    ordering = filters.OrderingFilter(
        fields=(
            ('id', 'id'),
            ('app_label', 'app_label'),
            ('model', 'model')
        )
    )

    class Meta:
        model = ContentType
        fields = {
            'id': filters.NUMBER_FILTER_TYPE,
            'app_label': filters.CHAR_FILTER_TYPE,
            'model': filters.CHAR_FILTER_TYPE
        }


class GroupFilter(filters.FilterSet):
    ordering = filters.OrderingFilter(
        fields=(
            ('id', 'id'),
            ('name', 'name')
        )
    )

    class Meta:
        model = Group
        fields = {
            'id': filters.NUMBER_FILTER_TYPE,
            'name': filters.CHAR_FILTER_TYPE
        }

class PermissionFilter(filters.FilterSet):
    ordering = filters.OrderingFilter(
        fields=(
            ('id', 'id'),
            ('name', 'name')
        )
    )

    class Meta:
        model = Permission
        fields = {
            'id': filters.NUMBER_FILTER_TYPE,
            'name': filters.CHAR_FILTER_TYPE
        }


class MessageFilter(filters.FilterSet):
    ordering = filters.OrderingFilter(
        fields=(
            ('id', 'id'),
            ('create_time', 'create_time'),
            ('title', 'title'),
            ('content_type', 'content_type'),
            ('object_id', 'object_id'),
        )
    )

    class Meta:
        model = models.Message
        fields = {
            'id': filters.NUMBER_FILTER_TYPE,
            'create_time': filters.DATETIME_FILTER_TYPE,
            'title': filters.CHAR_FILTER_TYPE,
            'content_type': filters.NUMBER_FILTER_TYPE,
            'object_id': filters.NUMBER_FILTER_TYPE
        }


class UserFilter(filters.FilterSet):
    ordering = filters.OrderingFilter(
        fields=(
            ('id', 'id'), ('username', 'username'),
            ('first_name', 'first_name'), ('last_name', 'last_name'),
            ('email', 'email')
        )
    )

    class Meta:
        model = User
        fields = {
            'id': filters.NUMBER_FILTER_TYPE,
            'username': filters.CHAR_FILTER_TYPE,
            'first_name': filters.CHAR_FILTER_TYPE,
            'last_name': filters.CHAR_FILTER_TYPE,
            'email': filters.CHAR_FILTER_TYPE
        }


class PartnerFilter(filters.FilterSet):

    class Meta:
        model = models.Partner
        fields = {
            'id': filters.NUMBER_FILTER_TYPE,
            'name': filters.CHAR_FILTER_TYPE,
            'phone': filters.CHAR_FILTER_TYPE,
            'address': filters.NUMBER_FILTER_TYPE,
            'default_send_address': filters.NUMBER_FILTER_TYPE,
            'is_company': filters.BOOLEAN_FILTER_TYPE,
            'sale_able': filters.BOOLEAN_FILTER_TYPE,
            'purchase_able': filters.BOOLEAN_FILTER_TYPE,
        }
