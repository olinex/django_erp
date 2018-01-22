#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
@author:    olinex
@time:      2017/11/13 上午12:07
"""

__all__ = ['ProvinceModelTestCase']

from ..models import Province
from django.test import TestCase
from django_erp.common.tests import DataModelTestCase


class ProvinceModelTestCase(TestCase, DataModelTestCase):
    model = Province

    def setUp(self):
        self.instance1 = self.model.objects.create(
            country='China',
            name='test1'
        )
        self.instance2 = self.model.objects.create(
            country='China',
            name='test2'
        )
        self.userSetup()

    def tearDown(self):
        self.userTearDown()
