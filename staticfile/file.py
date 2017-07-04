#!/usr/bin/env python2
# -*- coding:utf-8 -*-

import os
import xlrd
import xlwt
from datetime import datetime


class Excel(object):
    '''excel文件'''
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "odoo.settings")
    models = []
    serializer_classes = []

    class Meta:
        verbose_name = ''
        save_path = ''

    def __init__(self, workbook):
        try:
            self.workbook = xlrd.open_workbook(workbook)
        except:
            self.workbook = workbook

    @staticmethod
    def get_valid_value(cell):
        ctype = cell.ctype
        value = cell.value
        if ctype < 6:
            if ctype == 0:
                return None
            if ctype == 3:
                return datetime(*xlrd.xldate_as_tuple(
                    cell.value, cell.book.datemode
                ))
            if ctype == 4:
                return bool(value)
            if ctype == 5:
                return ValueError(value)
            return value
        else:
            raise AttributeError('无法识别的单元格数据类型')

    def sheet_field_names(self, index):
        return self.workbook.sheet_by_index(index).row_values(0)

    def sheet_verbose_names(self, index):
        return self.workbook.sheet_by_index(index).row_values(1)

    def sheet_fields(self, index):
        return dict(zip(
            self.sheet_field_names(index),
            self.sheet_verbose_names(index)
        ))

    def row(self, index, row_num):
        return map(
            self.get_valid_value,
            self.workbook.sheet_by_index(index).row(row_num)
        )

    def row_dict(self, index, row_num):
        return dict(
            zip(
                self.sheet_field_names(index),
                self.row(index, row_num)
            )
        )

    def rows(self, index, start_col=0, end_col=None):
        sheet = self.workbook.sheet_by_index(index)
        max_row = sheet.nrows
        return (
            map(self.get_valid_value, sheet.row(row_num)[start_col:end_col])
            for row_num in range(2, max_row)
        )

    def valid_row(self, index, row_num):
        serializer = self.serializer_classes[index](
            data=self.row_dict(index, row_num))
        if serializer.is_valid():
            return serializer.validated_data
        return serializer.errors

    def is_valid(self, pure=False):
        if not hasattr(self, '__valid_result'):
            self.__valid_result = True
            self.validated_data = []
            self.errors = []
            for index, serializer_class in enumerate(self.serializer_classes):
                sheet_field_names = self.sheet_field_names(index)
                validated_data = []
                errors = []
                row_index = 2
                for row in self.rows(index=index):
                    serializer = serializer_class(data=dict(zip(sheet_field_names, row)))
                    if serializer.is_valid() and not pure:
                        validated_data.append([row_index, serializer.validated_data])
                    else:
                        errors.append([row_index, serializer.errors])
                        self.__valid_result = False
                    row_index += 1
                if not pure:
                    self.validated_data.append(validated_data)
                self.errors.append(errors)
        return self.__valid_result

    def save_validated_data(self, force_insert=False):
        if self.is_valid() or force_insert:
            for index, model in enumerate(self.models):
                validated_data = self.validated_data[index]
                for data in validated_data:
                    model.objects.create(data)

    @classmethod
    def serializer_field_names(cls, index):
        return cls.serializer_classes[index].Meta.fields

    @classmethod
    def serializer_verbose_names(cls, index):
        serializer = cls.serializer_classes[index]()
        return [field.label for field in serializer.fields.values()]

    @classmethod
    def template_header(cls, index):
        return [
            cls.serializer_field_names(index),
            cls.serializer_verbose_names(index)
        ]

    @classmethod
    def create_template(cls, stream=None):
        template_path = os.path.join(
            cls.Meta.save_path or '',
            '{}_template.xls'.format(str(getattr(cls.Meta, 'verbose_name', None) or cls.__name__))
        )
        if not stream and os.path.exists(template_path):
            return None
        file = xlwt.Workbook()
        for i, serializer in enumerate(cls.serializer_classes):
            sheet = file.add_sheet(str(getattr(serializer.Meta, 'verbose_name', None) or i))
            for col, field_name in enumerate(cls.serializer_field_names(i)):
                sheet.write(0, col, field_name)
            for col, verbose_name in enumerate(cls.serializer_verbose_names(i)):
                sheet.write(1, col, verbose_name)
        file.save(stream or template_path)