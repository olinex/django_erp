#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
@author:    olinex
@time:      2017/11/12 下午8:25
"""

__all__ = ['CityViewSet']

from .. import models, serializers, filters
from django_erp.rest.viewsets import DataViewSet

class CityViewSet(DataViewSet):
    model = models.City
    serializer_class = serializers.CitySerializer
    filter_class = filters.CityFilter

    def get_queryset(self):
        return self.model.objects.select_related('province').all()