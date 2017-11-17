#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
@author:    olinex
@time:      2017/8/30 下午1:38
"""

__all__ = [
    'StateInstanceValidator',
    'NotZeroValidator',
    'ActiveStateValidator',
    'NoActiveStateValidator',
    'IPPortValidator'
]

from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.utils.deconstruct import deconstructible
from django.core.validators import MaxValueValidator


@deconstructible
class StateInstanceValidator(object):
    message = _('Ensure this instance %(instance)s is in %(states)s.')
    code = 'state_instance'

    def __init__(self, *states):
        self.states = set(states)

    def __call__(self, value):
        if not value.check_states(*self.states):
            raise ValidationError(
                self.message,
                code=self.code,
                params={'instance': value, 'states': ','.join(self.states)}
            )

    def __eq__(self, other):
        return (
            isinstance(other, self.__class__) and
            self.states == other.states and
            self.message == other.message and
            self.code == other.code
        )


def NotZeroValidator(value):
    """
    :param value: int/float/decimal
    :return: None
    :raise: ValidationError
    """
    if value == 0:
        raise ValidationError(
            _('%(value)s can not equal to zero'),
            params={'value': value}
        )

def IPPortValidator(value):
    """
        :param value: int
        :return: None
        :raise: ValidationError
        """
    if value > 65536:
        raise ValidationError(_('IP Port can not greater than 65536'))



ActiveStateValidator = StateInstanceValidator('active')
NoActiveStateValidator = StateInstanceValidator('no_active')
