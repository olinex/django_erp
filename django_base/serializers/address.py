#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
@author:    olinex
@time:      2017/11/12 下午3:35
"""

from .. import models
from .province import ProvinceSerializer
from .city import CitySerializer
from .region import RegionSerializer
from rest_framework import serializers
from django_erp.rest.fields import StatePrimaryKeyRelatedField


class AddressSerializer(serializers.ModelSerializer):
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
    region = StatePrimaryKeyRelatedField(
        'active',
        model=models.Region
    )

    class Meta:
        model = models.Address
        fields = '__all__'