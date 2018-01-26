#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
@author:    olinex
@time:      2017/11/17 下午10:30
"""

__all__ = ['ChangeViewSet']

from .. import models, serializers, filters
from django_erp.rest.viewsets import OrderViewSet


class ChangeViewSet(OrderViewSet):
    model = models.Change
    allow_actions = ('list', 'retrieve')
    serializer_class = serializers.ChangeSerializer
    filter_class = filters.ChangeFilter

    def get_queryset(self):
        return self.model.objects.select_related('content_type')
