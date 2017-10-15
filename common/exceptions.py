#!/usr/bin/env python3
# -*- coding:utf-8 -*-

'''
@author:    olinex
@time:      2017/8/24 下午3:51
'''

from django.core.exceptions import PermissionDenied

class NotInStates(PermissionDenied):

    def __init__(self,state,message):
        self.state = state
        self.message = message