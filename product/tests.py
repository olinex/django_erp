#!/usr/bin/env python3
#-*- coding:utf-8 -*-

import random, string
from . import models
from django.test import TestCase

class ProductCategory(TestCase):

    def setUp(self):
        self.instance = models.ProductCategory.objects.create(name='test')
        models.ProductCategory.objects.bulk_create([
            models.ProductCategory(name=name) for name in ['test1','test2','test3']
        ])
        self.queryset = models.ProductCategory.objects.all()

    def test_check_state(self):
        self.assertEqual(self.instance.check_state('delete'),False)
        self.assertEqual(self.instance.check_state('undelete'),True)
        self.assertEqual(self.instance.check_state('active'), True)
        self.assertEqual(self.instance.check_state('deactive'), False)

    def test_set_state(self):
        self.instance.set_state('delete')
        self.assertEqual(self.instance.is_delete,True)
        self.instance.set_state('undelete')
        self.assertEqual(self.instance.is_delete,False)
        self.instance.set_state('deactive')
        self.assertEqual(self.instance.is_active, False)
        self.instance.set_state('active')
        self.assertEqual(self.instance.is_active, True)

    def test_check_to_set_state(self):
        self.assertEqual(self.instance.check_to_set_state('undelete','delete'),True)
        self.assertEqual(self.instance.is_delete, True)
        self.assertEqual(self.instance.check_to_set_state('delete','undelete'),True)
        self.assertEqual(self.instance.is_delete, False)
        self.assertEqual(self.instance.check_to_set_state('active', 'deactive'), True)
        self.assertEqual(self.instance.is_active, False)
        self.assertEqual(self.instance.check_to_set_state('deactive', 'active'), True)
        self.assertEqual(self.instance.is_active, True)

    def test_check_state_queryset(self):
        self.assertEqual(models.ProductCategory.check_state_queryset('delete',self.queryset),False)
        self.assertEqual(models.ProductCategory.check_state_queryset('undelete',self.queryset),True)

    def test_set_state_queryset(self):
        models.ProductCategory.set_state_queryset('delete',self.queryset)
        self.assertEqual(models.ProductCategory.check_state_queryset('delete',self.queryset),True)
        models.ProductCategory.set_state_queryset('undelete',self.queryset)
        self.assertEqual(models.ProductCategory.check_state_queryset('undelete',self.queryset),True)

    def test_check_to_set_state_queryset(self):
        self.assertEqual(models.ProductCategory.check_to_set_state_queryset('undelete','delete',self.queryset),True)
        self.assertEqual(models.ProductCategory.check_to_set_state_queryset('delete', 'undelete',self.queryset),True)
