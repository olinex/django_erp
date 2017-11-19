#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
@author:    olinex
@time:      2017/11/14 下午3:14
"""

__all__ = ['get_argument']


def get_argument(name):
    """
    the enviroment argument by name
    :param name: string
    :return: int/string/boolean/list/dict/None
    """
    from .models import Argument
    argument = Argument.get_cache(name=name).get()
    if argument:
        return argument['value']
    return None
