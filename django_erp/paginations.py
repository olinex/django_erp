#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
@author:    olinex
@time:      2017/9/28 下午8:41
"""

from rest_framework import pagination

class DefaultPagination(pagination.PageNumberPagination):
    page_size = 10
    max_page_size = 100
    page_size_query_param = 'page_size'