#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
@author:    olinex
@time:      2017/11/12 下午3:41
"""

__all__ = ['StatePrimaryKeyRelatedField']

from rest_framework import serializers

class StatePrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):
    """the primary key field restrict by state"""

    def __init__(self,*states,model,**kwargs):
        super(StatePrimaryKeyRelatedField,self).__init__(
            queryset=model.get_states_queryset(*states),
            **kwargs
        )