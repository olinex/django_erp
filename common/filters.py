#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
@author:    olinex
@time:      2017/9/29 上午9:01
"""

TEXT_FILTER_TYPE = ['contains','icontains','exact','iexact']
NUMBER_FILTER_TYPE = ['exact','lt','lte','gt','gte']
BOOLEAN_FILTER_TYPE = ['exact']
SELECT_FILTER_TYPE = ['exact']
DATE_FILTER_TYPE = ['date','date__gt','date__gte','date__lt','date__lte']
TIME_FILTER_TYPE = ['time','time__gt','time__gte','time__lt','time__lte']
DATETIME_FILTER_TYPE = ['exact','gt','gte','lt','lte']