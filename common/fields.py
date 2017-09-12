#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from django_perm import models
from common.validators import ActiveStateValidator


class ActiveLimitForeignKey(models.ForeignKey):
    '''可用外键约束'''

    def __init__(self, *args, **kwargs):
        kwargs['limit_choices_to'] = kwargs.get('limit_choices_to', {'is_delete': False, 'is_active': True})
        kwargs['on_delete'] = kwargs.get('on_delete', models.PROTECT)
        kwargs['validators'] = kwargs.get('validators', [ActiveStateValidator])
        super(ActiveLimitForeignKey, self).__init__(*args, **kwargs)


class ActiveLimitOneToOneField(models.OneToOneField):
    '''可用外键约束'''

    def __init__(self, *args, **kwargs):
        kwargs['limit_choices_to'] = kwargs.get('limit_choices_to', {'is_delete': False, 'is_active': True})
        kwargs['on_delete'] = kwargs.get('on_delete', models.PROTECT)
        kwargs['validators'] = kwargs.get('validators', [ActiveStateValidator])
        super(ActiveLimitOneToOneField, self).__init__(*args, **kwargs)


class ActiveLimitManyToManyField(models.ManyToManyField):
    '''可用外键约束'''

    def __init__(self, *args, **kwargs):
        kwargs['limit_choices_to'] = kwargs.get('limit_choices_to', {'is_delete': False, 'is_active': True})
        super(ActiveLimitManyToManyField, self).__init__(*args, **kwargs)


class MD5CharField(models.CharField):
    '''md5字符串字段,自动将输入的utf8字符串转换为md5值并保存'''

    def get_prep_value(self, value):
        from hashlib import md5
        m = md5()
        m.update(value.encode('utf8'))
        return m.hexdigest()


class SimpleStateCharField(models.CharField):
    def __init__(self, *args, **kwargs):
        kwargs['choices'] = kwargs.get(
            'choices',
            (
                ('draft', '草稿'),
                ('confirmed', '已确定'),
                ('done', '已完成')
            )
        )
        kwargs['null'] = kwargs.get('null',False)
        kwargs['blank'] = kwargs.get('blank',False)
        kwargs['default'] = 'draft'
        kwargs['max_length'] = kwargs.get('max_length',10)
        super(SimpleStateCharField, self).__init__(*args, **kwargs)


class CancelableSimpleStateCharField(models.CharField):
    def __init__(self, *args, **kwargs):
        kwargs['choices'] = kwargs.get(
            'choices',
            (
                ('draft', '草稿'),
                ('confirmed', '已确定'),
                ('done', '已完成'),
                ('cancel','取消'),
            )
        )
        kwargs['null'] = kwargs.get('null',False)
        kwargs['blank'] = kwargs.get('blank',False)
        kwargs['default'] = 'draft'
        kwargs['max_length'] = kwargs.get('max_length',10)
        super(CancelableSimpleStateCharField, self).__init__(*args, **kwargs)


class BaseStateCharField(models.CharField):
    def __init__(self, *args, **kwargs):
        kwargs['choices'] = kwargs.get(
            'choices',
            (
                ('draft', '草稿'),
                ('confirmed', '已确定'),
                ('assigned', '已指派'),
                ('accepted', '已接受'),
                ('done', '已完成')
            )
        )
        kwargs['null'] = kwargs.get('null', False)
        kwargs['blank'] = kwargs.get('blank', False)
        kwargs['max_length'] = kwargs.get('max_length', 10)
        super(BaseStateCharField, self).__init__(*args, **kwargs)


class FullStateCharField(models.CharField):
    def __init__(self, *args, **kwargs):
        kwargs['choices'] = kwargs.get(
            'choices',
            (
                ('draft', '草稿'),
                ('confirmed', '已确定'),
                ('assigned', '已指派'),
                ('accepted', '已接受'),
                ('approving','审批中'),
                ('approved', '已审批'),
                ('done', '已完成')
            )
        )
        kwargs['null'] = kwargs.get('null', False)
        kwargs['blank'] = kwargs.get('blank', False)
        kwargs['max_length'] = kwargs.get('max_length', 10)
        super(FullStateCharField, self).__init__(*args, **kwargs)
