#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
@author:    olinex
@time:      2017/11/13 下午7:39
"""

__all__ = ['PartnerModelTestCase']

from ..models import Partner
from django.test import TestCase
from django_erp.common.tests import BaseModelTestCase


class PartnerModelTestCase(TestCase, BaseModelTestCase):
    model = Partner

    def setUp(self):
        self.instance1 = self.model.objects.create(
            name='test1',
            phone='123456'
        )
        self.instance2 = self.model.objects.create(
            name='test2',
            phone='123456'
        )
