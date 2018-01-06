#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Created on 2016年9月4日

@author: olin
"""

__all__ = [
    'ConfirmModelMixin',
    'LockModelMixin',
    'ActiveModelMixin',
    'DeleteModelMixin',
    'DoneModelMixin',
    'CancelModelMixin',
    'AuditModelMixin',
    'RejectModelMixin',
    'AllowedModelMixin'
]

from .serializers import IdListSerializer
from rest_framework.decorators import list_route
from rest_framework.response import Response
from django.utils.translation import ugettext_lazy as _


class ConfirmModelMixin(object):
    """
    contain the method for confirm model
    """

    @list_route(['patch'], serializer_class=IdListSerializer)
    def confirm(self, request):
        serializer = getattr(self, 'get_serializer')(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)
        ids = serializer.validated_data['ids']
        queryset = getattr(self, 'get_queryset')().filter(id__in=ids)
        for instance in queryset:
            instance.action_confirm(raise_exception=True)
        return Response({'detail': _('confirm successfully')})


class LockModelMixin(object):
    """
    contain the method for lock model
    """

    @list_route(['patch'], serializer_class=IdListSerializer)
    def lock(self, request):
        serializer = getattr(self, 'get_serializer')(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)
        ids = serializer.validated_data['ids']
        queryset = getattr(self, 'get_queryset')().filter(id__in=ids)
        for instance in queryset:
            instance.action_lock(raise_exception=True)
        return Response({'detail': _('confirm successfully')})


class ActiveModelMixin(object):
    """
    contain the method for active model
    """

    @list_route(['patch'], serializer_class=IdListSerializer)
    def active(self,request):
        serializer = getattr(self,'get_serializer')(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)
        ids = serializer.validated_data['ids']
        queryset = getattr(self,'get_queryset')().filter(id__in=ids)
        for instance in queryset:
            instance.action_active(raise_exception=True)
        return Response({'detail': _('active successfully')})


class DeleteModelMixin(object):
    """delete the instance using model's action_delete method"""

    @list_route(['patch'], serializer_class=IdListSerializer)
    def delete(self, request):
        serializer = getattr(self, 'get_serializer')(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)
        ids = serializer.validated_data['ids']
        queryset = getattr(self, 'get_queryset')().filter(id__in=ids)
        for instance in queryset:
            instance.action_delete(raise_exception=True)
        return Response({'detail': _('delete successfully')})


class DoneModelMixin(object):
    """
    contain the method for done model
    """

    @list_route(['patch'], serializer_class=IdListSerializer)
    def do(self, request):
        serializer = getattr(self, 'get_serializer')(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)
        ids = serializer.validated_data['ids']
        queryset = getattr(self, 'get_queryset')().filter(id__in=ids)
        for instance in queryset:
            instance.action_do(raise_exception=True)
        return Response({'detail': _('do successfully')})


class CancelModelMixin(object):
    """
    contain the method for cancel model
    """

    @list_route(['patch'], serializer_class=IdListSerializer)
    def cancel(self, request):
        serializer = getattr(self, 'get_serializer')(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)
        ids = serializer.validated_data['ids']
        queryset = getattr(self, 'get_queryset')().filter(id__in=ids)
        for instance in queryset:
            instance.action_cancel(raise_exception=True)
        return Response({'detail': _('cancel successfully')})


class AuditModelMixin(object):
    """
    contain the method for audit model
    """

    @list_route(['patch'], serializer_class=IdListSerializer)
    def audit(self, request):
        serializer = getattr(self, 'get_serializer')(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)
        ids = serializer.validated_data['ids']
        queryset = getattr(self, 'get_queryset')().filter(id__in=ids)
        for instance in queryset:
            instance.action_audit(raise_exception=True)
        return Response({'detail': _('audit successfully')})


class RejectModelMixin(object):
    """
    contain the method for reject model
    """

    @list_route(['patch'], serializer_class=IdListSerializer)
    def reject(self, request):
        serializer = getattr(self, 'get_serializer')(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)
        ids = serializer.validated_data['ids']
        queryset = getattr(self, 'get_queryset')().filter(id__in=ids)
        for instance in queryset:
            instance.action_reject(raise_exception=True)
        return Response({'detail': _('reject successfully')})


class AllowedModelMixin(object):
    """
    contain the method for allowed model
    """

    @list_route(['patch'], serializer_class=IdListSerializer)
    def allow(self, request):
        serializer = getattr(self, 'get_serializer')(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)
        ids = serializer.validated_data['ids']
        queryset = getattr(self, 'get_queryset')().filter(id__in=ids)
        for instance in queryset:
            instance.action_allow(raise_exception=True)
        return Response({'detail': _('allow successfully')})
