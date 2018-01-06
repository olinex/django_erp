#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
@author:    olinex
@time:      2017/11/15 下午2:29
"""

__all__ = ['MessageModelTestCase','UserModelTestCase']

import random
import string
from django.test import tag
from django_base.utils import get_argument
from django_erp.common.tests import AbstractTestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser

User = get_user_model()


class UserModelTestCase(AbstractTestCase):
    """class for provide test user"""
    def userSetUp(self):
        self.password = ''.join(random.sample(string.ascii_letters, 10))
        self.super_user = User.objects.create_superuser(
            username='test_super_user',
            email='demosuperuser@163.com',
            password=self.password)
        self.normal_user = User.objects.create_user(
            username='test_normal_user',
            email='demouser@163.com',
            password=self.password)
        self.anon_user = AnonymousUser()

    def userTearDown(self):
        self.super_user.clear_messages()
        self.normal_user.clear_messages()


class MessageModelTestCase(UserModelTestCase):
    """class for testing the message system"""
    instance1 = instance2 = None

    @tag('buildin')
    def test_create_message_without_followers(self):
        self.super_user.clear_messages()
        self.normal_user.clear_messages()
        self.instance1.create_message(
            title='test',
            text='test message',
            creater=self.super_user
        )
        if get_argument('add_follower_after_create_message') is False:
            self.assertFalse(self.super_user.new_messages.exists())
        else:
            self.assertTrue(self.super_user.new_messages.exists())

    @tag('buildin')
    def test_create_message_with_single_follower(self):
        self.super_user.clear_messages()
        self.normal_user.clear_messages()
        self.assertIsNone(self.instance1.add_followers(self.normal_user))
        message = self.instance1.create_message(
            title='test',
            text='test message',
            creater=self.super_user
        )
        if get_argument('add_follower_after_create_message') is False:
            self.assertFalse(self.super_user.new_messages.exists())
            self.assertEqual(self.normal_user.new_messages.first(), message)
        else:
            self.assertTrue(self.super_user.new_messages.exists())
            self.assertEqual(self.super_user.new_messages.first(), message)
            self.assertEqual(self.normal_user.new_messages.first(), message)

    @tag('buildin')
    def test_create_message_with_multi_followers(self):
        self.super_user.clear_messages()
        self.normal_user.clear_messages()
        self.assertIsNone(self.instance1.add_followers(self.super_user, self.normal_user))
        message = self.instance1.create_message(
            title='test',
            text='test message',
            creater=self.super_user
        )
        self.assertEqual(self.normal_user.new_messages.first(), message)
        self.assertEqual(self.normal_user.new_messages.first(), message)
