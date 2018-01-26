#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
@author:    olinex
@time:      2018/1/6 上午12:19
"""

__all__ = ['PermissionViewSet']

from .. import filters
from django_erp.rest.serializers import PermissionsSerializer
from django.contrib.auth.models import Permission
from django_erp.rest.viewsets import PermMethodViewSet

class PermissionViewSet(PermMethodViewSet):
    model = Permission
    allow_actions = ('list', 'retrieve')
    serializer_class = PermissionsSerializer
    filter_class = filters.PermissionFilter

    def get_queryset(self):
        return self.model.objects.select_related('content_type')