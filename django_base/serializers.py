#!/usr/bin/env python3
# -*- coding:utf-8 -*-

'''
@author:    olinex
@time:      2017/9/26 下午1:23
'''

from rest_framework import serializers

from common.rest.serializers import ActiveModelSerializer
from . import models

class ProvinceSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Province
        fields = ('id', 'country', 'name')


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.City
        fields = ('id', 'province', 'name')


class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Region
        fields = ('id', 'city', 'name')


class AddressSerializer(ActiveModelSerializer):
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
        fields = (
            'id', 'region', 'name', 'is_active',
            'province_detail', 'city_detail', 'region_detail'
        )