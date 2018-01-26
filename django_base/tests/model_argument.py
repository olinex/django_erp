#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
@author:    olinex
@time:      2017/11/13 下午10:30
"""

__all__ = ['ArgumentModelTestCase']

from ..models import Argument
from django.test import TestCase


class ArgumentModelTestCase(TestCase):
    model = Argument
    fixtures = ['argument']

    def setUp(self):
        self.userSetup()
        self.data1 = [1, 2, 3, 4]
        self.data2 = {'a': 1, 'b': 2, 'c': 3, 'd': 4}
        self.instance1 = self.model.objects.create(
            name='data1',
            value=self.data1,
            sequence=1
        )
        self.instance2 = self.model.objects.create(
            name='data2',
            value=self.data2,
            sequence=2
        )

    def tearDown(self):
        self.userTearDown()
        self.instance1.get_cache('data1').delete()
        self.instance2.get_cache('data2').delete()
