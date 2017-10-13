#!/usr/bin/env python3
#-*- coding:utf-8 -*-

from . import models
from common.filters import TEXT_FILTER_TYPE,NUMBER_FILTER_TYPE,BOOLEAN_FILTER_TYPE
from django_filters import rest_framework as filters

class UserFilter(filters.FilterSet):
    ordering = filters.OrderingFilter(
        fields=(
            ('id','id'),('username','username'),
            ('first_name','first_name'),('last_name','last_name'),
            ('email','email')
        )
    )
    class Meta:
        model = models.User
        fields = {
            'id':NUMBER_FILTER_TYPE,
            'username':TEXT_FILTER_TYPE,
            'email':TEXT_FILTER_TYPE,
            'is_active':BOOLEAN_FILTER_TYPE
        }