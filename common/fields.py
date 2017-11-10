#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from django_perm import models
from common.validators import ActiveStateValidator
from django.utils.translation import ugettext_lazy as _


class ActiveLimitForeignKey(models.ForeignKey):
    """the foreignkey to instance that are active"""

    def __init__(self, *args, **kwargs):
        kwargs['limit_choices_to'] = kwargs.get('limit_choices_to', {'is_delete': False, 'is_active': True})
        kwargs['on_delete'] = kwargs.get('on_delete', models.PROTECT)
        kwargs['validators'] = kwargs.get('validators', [ActiveStateValidator])
        super(ActiveLimitForeignKey, self).__init__(*args, **kwargs)


class ActiveLimitOneToOneField(models.OneToOneField):
    """the one to one field to instance that are active"""

    def __init__(self, *args, **kwargs):
        kwargs['limit_choices_to'] = kwargs.get('limit_choices_to', {'is_delete': False, 'is_active': True})
        kwargs['on_delete'] = kwargs.get('on_delete', models.PROTECT)
        kwargs['validators'] = kwargs.get('validators', [ActiveStateValidator])
        super(ActiveLimitOneToOneField, self).__init__(*args, **kwargs)


class MD5CharField(models.CharField):
    """the char field will automatically convert string to md5 string"""

    def get_prep_value(self, value):
        from hashlib import md5
        m = md5()
        m.update(value.encode('utf8'))
        return m.hexdigest()

class OrderStateCharField(models.CharField):
    def __init__(self, *args, **kwargs):
        kwargs['choices'] = kwargs.get(
            'choices',
            (
                ('draft', _('draft')),
                ('confirmed', _('confirmed')),
                ('done', _('done'))
            )
        )
        kwargs['null'] = kwargs.get('null', False)
        kwargs['blank'] = kwargs.get('blank', False)
        kwargs['default'] = 'draft'
        kwargs['max_length'] = kwargs.get('max_length', 10)
        super(OrderStateCharField, self).__init__(*args, **kwargs)


class AuditStateCharField(models.CharField):
    def __init__(self, *args, **kwargs):
        kwargs['choices'] = kwargs.get(
            'choices',
            (
                ('draft', _('draft')),
                ('confirmed', _('confirmed')),
                ('reject', _('reject'))
            )
        )
        kwargs['null'] = kwargs.get('null', False)
        kwargs['blank'] = kwargs.get('blank', False)
        kwargs['default'] = 'draft'
        kwargs['max_length'] = kwargs.get('max_length', 10)
        super(AuditStateCharField, self).__init__(*args, **kwargs)


class SimpleStateCharField(models.CharField):
    def __init__(self, *args, **kwargs):
        kwargs['choices'] = kwargs.get(
            'choices',
            (
                ('draft', _('draft')),
                ('confirmed', _('confirmed')),
                ('done', _('done'))
            )
        )
        kwargs['null'] = kwargs.get('null', False)
        kwargs['blank'] = kwargs.get('blank', False)
        kwargs['default'] = 'draft'
        kwargs['max_length'] = kwargs.get('max_length', 10)
        super(SimpleStateCharField, self).__init__(*args, **kwargs)


class CancelableSimpleStateCharField(models.CharField):
    def __init__(self, *args, **kwargs):
        kwargs['choices'] = kwargs.get(
            'choices',
            (
                ('draft', _('draft')),
                ('confirmed', _('confirmed')),
                ('done', _('done')),
                ('cancel', _('cancel')),
            )
        )
        kwargs['null'] = kwargs.get('null', False)
        kwargs['blank'] = kwargs.get('blank', False)
        kwargs['default'] = 'draft'
        kwargs['max_length'] = kwargs.get('max_length', 10)
        super(CancelableSimpleStateCharField, self).__init__(*args, **kwargs)


class BaseStateCharField(models.CharField):
    def __init__(self, *args, **kwargs):
        kwargs['choices'] = kwargs.get(
            'choices',
            (
                ('draft', _('draft')),
                ('confirmed', _('confirmed')),
                ('assigned', _('assigned')),
                ('accepted', _('accepted')),
                ('done', _('done'))
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
                ('draft', _('draft')),
                ('confirmed', _('confirmed')),
                ('assigned', _('assigned')),
                ('accepted', _('accepted')),
                ('approved', _('approved')),
                ('approving', _('approving')),
                ('done', _('done')),
            )
        )
        kwargs['null'] = kwargs.get('null', False)
        kwargs['blank'] = kwargs.get('blank', False)
        kwargs['max_length'] = kwargs.get('max_length', 10)
        super(FullStateCharField, self).__init__(*args, **kwargs)
