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

from rest_framework.decorators import detail_route
from rest_framework.mixins import DestroyModelMixin
from rest_framework.response import Response
from django.utils.translation import ugettext_lazy as _


class ConfirmModelMixin(object):
    """
    contain the method for confirm model
    """

    @detail_route(['patch'])
    def confirm(self, request, pk=None):
        """turn state to confirm"""
        instance = getattr(self, 'get_object')()
        instance.action_confirm(raise_exception=True)
        return Response({'detail': _('confirm successfully')})


class LockModelMixin(object):
    """
    contain the method for lock model
    """

    @detail_route(['patch'])
    def lock(self, request, pk=None):
        """turn state to confirm"""
        instance = getattr(self, 'get_object')()
        instance.action_lock(raise_exception=True)
        return Response({'detail': _('lock successfully')})


class ActiveModelMixin(object):
    """
    contain the method for active model
    """

    @detail_route(['patch'])
    def active(self, request, pk=None):
        """turn state to active"""
        instance = getattr(self, 'get_object')()
        instance.action_active(raise_exception=True)
        return Response({'detail': _('active successfully')})


class DeleteModelMixin(DestroyModelMixin):
    """delete the instance using model's action_delete method"""

    def perform_destroy(self, instance):
        instance.action_delete()


class DoneModelMixin(object):
    """
    contain the method for done model
    """

    @detail_route(['patch'])
    def done(self, request, pk=None):
        """turn state to done"""
        instance = getattr(self, 'get_object')()
        instance.action_done(raise_exception=True)
        return Response({'detail': _('done successfully')})


class CancelModelMixin(object):
    """
    contain the method for cancel model
    """

    @detail_route(['patch'])
    def cancel(self, request, pk=None):
        """turn state to cancel"""
        instance = getattr(self, 'get_object')()
        instance.action_cancel(raise_exception=True)
        return Response({'detail': _('cancel successfully')})


class AuditModelMixin(object):
    """
    contain the method for audit model
    """

    @detail_route(['patch'])
    def audit(self, request, pk=None):
        """turn state to audit"""
        instance = getattr(self, 'get_object')()
        instance.action_audit(raise_exception=True)
        return Response({'detail': _('audit successfully')})


class RejectModelMixin(object):
    """
    contain the method for reject model
    """

    @detail_route(['patch'])
    def reject(self, request, pk=None):
        """turn state to reject"""
        instance = getattr(self, 'get_object')()
        instance.action_reject(raise_exception=True)
        return Response({'detail': _('reject successfully')})


class AllowedModelMixin(object):
    """
    contain the method for allowed model
    """

    @detail_route(['patch'])
    def allowed(self, request, pk=None):
        """turn state to allowed"""
        instance = getattr(self, 'get_object')()
        instance.action_allowed(raise_exception=True)
        return Response({'detail': _('allowed successfully')})
