#!/usr/bin/env python3
# -*- coding:utf-8 -*-

'''
@author:    olinex
@time:      2017/8/30 下午1:38
'''

from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.utils.deconstruct import deconstructible


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
    '''
    :param value: int/float/decimal
    :return: None
    :raise: ValidationError
    '''
    if value == 0:
        raise ValidationError(
            _('%(value)s can not equal to zero'),
            params={'value': value}
        )


ActiveStateValidator = StateInstanceValidator('active')
DeleteStateValidator = StateInstanceValidator('delete')
NoActiveStateValidator = StateInstanceValidator('no_active')
NoDeleteStateValidator = StateInstanceValidator('no_delete')
