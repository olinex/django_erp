#!/usr/bin/env python3
#-*- coding:utf-8 -*-

from . import models
from django.urls import reverse
from rest_framework import status
from common.test import EnvSetUpTestCase

class SignalTestCase(EnvSetUpTestCase):

    def test_create_profile(self):
        self.assertTrue(models.Profile.objects.get(user=self.superuser))
        self.assertTrue(models.Profile.objects.get(user=self.normaluser))

class CeleryTestCase(EnvSetUpTestCase):

    def test_send_email(self):
        from .tasks import send_email
        res=send_email.delay(
            title='test',
            message='test message',
            to_emails=('djangoerp@163.com',),
            username='demo-user'
        )
