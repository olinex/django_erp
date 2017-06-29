#!/usr/bin/env python3
#-*- coding:utf-8 -*-

import random
import string
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser

User=get_user_model()

class UserSetUpTestCase(TestCase):

    def setUp(self):
        self.passwd = ''.join(random.sample(string.ascii_letters, 10))
        self.superuser = User.objects.create_superuser(
            username='testsuperuser',
            email='demosuperuser@163.com',
            password=self.passwd)
        self.normaluser = User.objects.create_user(
            username='testnormaluser',
            email='demouser@163.com',
            password=self.passwd)
        self.anonuser = AnonymousUser()