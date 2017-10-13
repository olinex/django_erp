#!/usr/bin/env python3
#-*- coding:utf-8 -*-

'''
@author:    olinex
@time:      2017/9/30 上午1:25
'''

from . import models
from common import filters as filter_types
from django_filters import rest_framework as filters

class ProvinceFilter(filters.FilterSet):
    ordering = filters.OrderingFilter(
        fields={
            'id':'id',
            'name':'name'
        }
    )
    class Meta:
        model = models.Province
        fields = {
            'id':filter_types.NUMBER_FILTER_TYPE,
            'country':filter_types.SELECT_FILTER_TYPE,
            'name':filter_types.TEXT_FILTER_TYPE
        }