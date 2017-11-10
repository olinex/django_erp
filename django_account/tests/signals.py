#!/usr/bin/env python3
# -*- coding:utf-8 -*-

__all__ = [
    'SignalTestCase',
]

from .. import models
from common.tests import EnvSetUpTestCase

class SignalTestCase(EnvSetUpTestCase):

    def setUp(self):
        self.accountSetUp()

    def test_create_profile(self):
        self.assertTrue(models.Profile.objects.get(user=self.super_user))
        self.assertTrue(models.Profile.objects.get(user=self.normal_user))
