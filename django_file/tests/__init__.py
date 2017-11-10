#!/usr/bin/env python3
# -*- coding:utf-8 -*-


import unittest
from . import file
from rest_framework import serializers


# class TestExcel(file.Excel):
#     class TestSerializer(serializers.Serializer):
#         test_int = serializers.IntegerField(label='测试整数')
#         test_char = serializers.CharField(label='测试字符串')
#
#         class Meta:
#             verbose_name = 'test'
#             fields = ('test_int', 'test_char')
#
#     serializer_classes = [TestSerializer]
#
#     class Meta:
#         verbose_name = ''
#         save_path = r'F:\workspace\common'
#
#
# class ExcelTestCase(unittest.TestCase):
#     def setUp(self):
#         self.path = r'F:\workspace\common\test.xlsx'
#         self.workbook = TestExcel(workbook=self.path)
#
#     def test_sheet_field_names(self):
#         self.assertEqual(self.workbook.sheet_field_names(0), ['test_int', 'test_char'])
#
#     def test_sheet_verbose_names(self):
#         self.assertEqual(self.workbook.sheet_verbose_names(0), ['测试整数', '测试字符串'])
#
#     def test_sheet_fields(self):
#         self.assertEqual(
#             self.workbook.sheet_fields(0),
#             {'test_int': '测试整数', 'test_char': '测试字符串'}
#         )
#
#     def test_row(self):
#         self.assertEqual(self.workbook.row(0, 2), [1, 'char1'])
#         self.assertEqual(self.workbook.row(0, 3), [2, 'char2'])
#
#     def test_row_dict(self):
#         self.assertEqual(self.workbook.row_dict(0, 2), {'test_int': 1, 'test_char': 'char1'})
#         self.assertEqual(self.workbook.row_dict(0, 3), {'test_int': 2, 'test_char': 'char2'})
#
#     def test_valid_row(self):
#         self.assertEqual(self.workbook.valid_row(0, 2), {'test_int': 1, 'test_char': 'char1'})
#         self.assertEqual(self.workbook.valid_row(0, 3), {'test_int': 2, 'test_char': 'char2'})
#
#     def test_is_valid(self):
#         self.assertTrue(self.workbook.is_valid())
#
#     def test_serializer_field_names(self):
#         self.assertEqual(self.workbook.serializer_field_names(0), ('test_int', 'test_char'))
#
#     def test_serializer_verbose_names(self):
#         self.assertEqual(self.workbook.serializer_verbose_names(0), ['测试整数', '测试字符串'])
#
#     def test_create_template(self):
#         import os
#         TestExcel.create_template()
#         self.assertTrue(os.path.exists(r'F:\workspace\common\TestExcel_template.xls'))
#

