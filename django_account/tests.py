#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from . import models
from common.tests import EnvSetUpTestCase

class SignalTestCase(EnvSetUpTestCase):

    def setUp(self):
        self.accountSetUp()

    def test_create_profile(self):
        self.assertTrue(models.Profile.objects.get(user=self.super_user))
        self.assertTrue(models.Profile.objects.get(user=self.normal_user))

# class CeleryTestCase(EnvSetUpTestCase):
#
#     def test_send_email(self):
#         from .tasks import send_email
#         res=send_email.delay(
#             title='test',
#             message='test message',
#             to_emails=('djangoerp@163.com',),
#             username='demo-user'
#         )
