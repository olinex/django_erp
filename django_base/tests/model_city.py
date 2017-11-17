#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
@author:    olinex
@time:      2017/11/13 下午5:39
"""

__all__ = ['CityModelTestCase']

from ..models import City, Province
from django.test import TestCase
from django_erp.common.tests import DataModelTestCase


class CityModelTestCase(TestCase, DataModelTestCase):
    model = City

    def setUp(self):
        province = Province.objects.create(country='China', name='test')
        self.instance1 = self.model.objects.create(
            province=province,
            name='test1'
        )
        self.instance2 = self.model.objects.create(
            province=province,
            name='test2'
        )
