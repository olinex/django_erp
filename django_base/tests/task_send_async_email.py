#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
@author:    olinex
@time:      2017/11/17 上午11:49
"""

__all__ = ['SendAsyncEmailTestCase']

from django.conf import settings
from django.test import TestCase
from ..tasks import send_async_email
from .abstract_test_case import UserModelTestCase

class SendAsyncEmailTestCase(TestCase,UserModelTestCase):

    def setUp(self):
        self.userSetUp()

    def tearDown(self):
        self.userTearDown()

    def test_send_default_email(self):
        send_async_email.delay(
            user_pk=self.super_user.pk,
            title='test',
            message='test',
            from_email=settings.DEFAULT_FROM_EMAIL,
            to_emails=[settings.DEFAULT_FROM_EMAIL],
            context={'title':'test','message':'test','user':self.super_user.username}
        )