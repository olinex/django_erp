#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
@author:    olinex
@time:      2017/9/30 上午1:25
"""

__all__ = [
    'ProvinceFilter',
    'UserFilter'
]

from . import models
from django.conf import settings
from django_filters import rest_framework as filters
from django.contrib.auth import get_user_model

User = get_user_model()


class ProvinceFilter(filters.FilterSet):
    ordering = filters.OrderingFilter(
        fields={
            'id': 'id',
            'name': 'name'
        }
    )

    class Meta:
        model = models.Province
        fields = {
            'id': settings.NUMBER_FILTER_TYPE,
            'country': settings.SELECT_FILTER_TYPE,
            'name': settings.TEXT_FILTER_TYPE
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
            'id': settings.NUMBER_FILTER_TYPE,
            'username': settings.TEXT_FILTER_TYPE,
            'email': settings.TEXT_FILTER_TYPE,
            'is_active': settings.BOOLEAN_FILTER_TYPE
        }
