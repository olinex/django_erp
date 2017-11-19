#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
@author:    olinex
@time:      2017/9/29 上午9:01
"""

__all__ = [
    'history_model_fields', 'base_model_fields', 'sequence_model_fields', 'data_model_fields', 'order_model_fields',
    'audit_order_model_fields', 'NumberFilter', 'CharFilter', 'BooleanFilter', 'ChoiceFilter', 'DateFilter',
    'DateTimeFilter', 'TimeFilter', 'OrderingFilter', 'FilterSet'
]

from django_filters import rest_framework as filters

CHAR_FILTER_TYPE = ['contains', 'icontains', 'exact', 'iexact']
NUMBER_FILTER_TYPE = ['exact', 'lt', 'lte', 'gt', 'gte']
BOOLEAN_FILTER_TYPE = ['exact']
CHOICE_FILTER_TYPE = ['exact']
DATE_FILTER_TYPE = ['date', 'date__gt', 'date__gte', 'date__lt', 'date__lte']
TIME_FILTER_TYPE = ['time', 'time__gt', 'time__gte', 'time__lt', 'time__lte']
DATETIME_FILTER_TYPE = ['exact', 'gt', 'gte', 'lt', 'lte']

OrderingFilter = filters.OrderingFilter
FilterSet = filters.FilterSet


class NumberFilter(filters.NumberFilter):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('lookup_expr', NUMBER_FILTER_TYPE)
        super(NumberFilter, self).__init__(*args, **kwargs)


class CharFilter(filters.CharFilter):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('lookup_expr', CHAR_FILTER_TYPE)
        super(CharFilter, self).__init__(*args, **kwargs)


class BooleanFilter(filters.BooleanFilter):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('lookup_expr', BOOLEAN_FILTER_TYPE)
        super(BooleanFilter, self).__init__(*args, **kwargs)


class ChoiceFilter(filters.ChoiceFilter):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('lookup_expr', CHOICE_FILTER_TYPE)
        super(ChoiceFilter, self).__init__(*args, **kwargs)


class DateFilter(filters.DateFilter):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('lookup_expr', DATE_FILTER_TYPE)
        super(DateFilter, self).__init__(*args, **kwargs)


class DateTimeFilter(filters.DateTimeFilter):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('lookup_expr', DATETIME_FILTER_TYPE)
        super(DateTimeFilter, self).__init__(*args, **kwargs)


class TimeFilter(filters.TimeFilter):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('lookup_expr', TIME_FILTER_TYPE)
        super(TimeFilter, self).__init__(*args, **kwargs)


class DateTimeFromToRangeFilter(filters.DateTimeFromToRangeFilter):
    pass


history_model_fields = {
    'id': NUMBER_FILTER_TYPE,
    'create_time': DATETIME_FILTER_TYPE,
    'last_modify_time': DATETIME_FILTER_TYPE,
}

base_model_fields = {
    'id': NUMBER_FILTER_TYPE,
    'create_time': DATETIME_FILTER_TYPE,
    'last_modify_time': DATETIME_FILTER_TYPE,
    'is_draft': BOOLEAN_FILTER_TYPE,
    'is_active': BOOLEAN_FILTER_TYPE,
}

sequence_model_fields = {
    'sequence': NUMBER_FILTER_TYPE
}

data_model_fields = {
    'id': NUMBER_FILTER_TYPE,
    'create_time': DATETIME_FILTER_TYPE,
    'last_modify_time': DATETIME_FILTER_TYPE,
    'is_draft': BOOLEAN_FILTER_TYPE,
    'is_active': BOOLEAN_FILTER_TYPE,
    'sequence': NUMBER_FILTER_TYPE
}

order_model_fields = {
    'id': NUMBER_FILTER_TYPE,
    'create_time': DATETIME_FILTER_TYPE,
    'last_modify_time': DATETIME_FILTER_TYPE,
    'is_draft': BOOLEAN_FILTER_TYPE,
    'is_active': BOOLEAN_FILTER_TYPE,
    'sequence': NUMBER_FILTER_TYPE,
    'state': CHOICE_FILTER_TYPE
}

audit_order_model_fields = {
    'id': NUMBER_FILTER_TYPE,
    'create_time': DATETIME_FILTER_TYPE,
    'last_modify_time': DATETIME_FILTER_TYPE,
    'is_draft': BOOLEAN_FILTER_TYPE,
    'is_active': BOOLEAN_FILTER_TYPE,
    'sequence': NUMBER_FILTER_TYPE,
    'state': CHOICE_FILTER_TYPE,
    'audit_state': CHOICE_FILTER_TYPE
}
