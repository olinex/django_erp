#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
@author:    olinex
@time:      2017/11/13 下午5:39
"""

__all__ = ['RegionModelTestCase']

from ..models import Region, City, Province
from django.test import TestCase
from django_erp.common.tests import DataModelTestCase


class RegionModelTestCase(TestCase, DataModelTestCase):
    model = Region

    def setUp(self):
        province = Province.objects.create(country='China', name='test')
        city = City.objects.create(province=province, name='test')
        self.instance1 = self.model.objects.create(
            city=city,
            name='test1'
        )
        self.instance2 = self.model.objects.create(
            city=city,
            name='test2'
        )
