#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
@author:    olinex
@time:      2017/11/12 下午3:35
"""

from .. import models
from django_erp.rest.serializers import DataModelSerializer
from .province import ProvinceSerializer
from .city import CitySerializer
from .region import RegionSerializer


class AddressSerializer(DataModelSerializer):
    province_detail = ProvinceSerializer(
        source='region.city.province',
        read_only=True
    )
    city_detail = CitySerializer(
        source='region.city',
        read_only=True
    )
    region_detail = RegionSerializer(
        source='region',
        read_only=True
    )

    class Meta:
        model = models.Address
        fields = '__all__'