#!/usr/bin/env python3
# -*- coding:utf-8 -*-

__all__ = [
    'ActiveOneToOneField',
    'ActiveForeignKey',
    'MD5CharField',
    'AuditStateCharField',
    'OrderStateCharField'
]

from django_perm.db import models
from .validators import ActiveStateValidator
from django.utils.translation import ugettext_lazy as _


class ActiveForeignKey(models.ForeignKey):
    """the foreignkey to instance that are active"""

    def __init__(self, *args, **kwargs):
        kwargs['limit_choices_to'] = kwargs.get('limit_choices_to', {'is_draft': False, 'is_active': True})
        kwargs['on_delete'] = kwargs.get('on_delete', models.PROTECT)
        kwargs['validators'] = kwargs.get('validators', [ActiveStateValidator])
        super(ActiveForeignKey, self).__init__(*args, **kwargs)


class ActiveOneToOneField(models.OneToOneField):
    """the one to one field to instance that are active"""

    def __init__(self, *args, **kwargs):
        kwargs['limit_choices_to'] = kwargs.get('limit_choices_to', {'is_draft': False, 'is_active': True})
        kwargs['on_delete'] = kwargs.get('on_delete', models.PROTECT)
        kwargs['validators'] = kwargs.get('validators', [ActiveStateValidator])
        super(ActiveOneToOneField, self).__init__(*args, **kwargs)


class MD5CharField(models.CharField):
    """the char field will automatically convert string to md5 string"""

    def get_prep_value(self, value):
        from hashlib import md5
        m = md5()
        m.update(value.encode('utf8'))
        return m.hexdigest()


class AuditStateCharField(models.CharField):
    def __init__(self, *args, **kwargs):
        kwargs['choices'] = kwargs.get(
            'choices',
            (
                ('waiting', _('waiting')),
                ('auditing', _('auditing')),
                ('rejected', _('rejected')),
                ('allowed', _('allowed'))
            )
        )
        kwargs['null'] = kwargs.get('null', False)
        kwargs['blank'] = kwargs.get('blank', False)
        kwargs['default'] = 'waiting'
        kwargs['max_length'] = kwargs.get('max_length', 10)
        super(AuditStateCharField, self).__init__(*args, **kwargs)


class OrderStateCharField(models.CharField):
    def __init__(self, *args, **kwargs):
        kwargs['choices'] = kwargs.get(
            'choices',
            (
                ('waiting', _('waiting')),
                ('confirmed', _('confirmed')),
                ('done', _('done')),
                ('cancelled', _('cancelled'))
            )
        )
        kwargs['null'] = kwargs.get('null', False)
        kwargs['blank'] = kwargs.get('blank', False)
        kwargs['default'] = 'waiting'
        kwargs['max_length'] = kwargs.get('max_length', 10)
        super(OrderStateCharField, self).__init__(*args, **kwargs)
