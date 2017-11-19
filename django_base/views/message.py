#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
@author:    olinex
@time:      2017/11/17 下午11:02
"""

__all__ = ['MessageViewSet']

from .. import models, serializers, filters
from django_erp.rest.viewsets import PermMethodViewSet


class MessageViewSet(PermMethodViewSet):
    model = models.Message
    allow_actions = ('list', 'retrieve')
    serializer_class = serializers.MessageSerializer
    filter_class = filters.MessageFilter

    def get_queryset(self):
        return self.model.objects.select_related('creater').all()
