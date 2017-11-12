#!/usr/bin/env python3
# -*- coding:utf-8 -*-

__all__ = [
    'PermMethodViewSet',
    'BaseViewSet',
    'DataViewSet',
    'OrderViewSet',
    'AuditOrderViewSet'
]

from rest_framework import mixins, exceptions, viewsets
from . import mixins as self_mixins


class PermMethodViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    """check the model have the right to make action"""
    allow_actions = ('create', 'list', 'retrieve', 'update', 'destroy')

    def get_queryset(self):
        return self.queryset if self.queryset else self.model.objects.all()

    def create(self, request, *args, **kwargs):
        if 'create' in self.allow_actions:
            return super(PermMethodViewSet, self).create(request, *args, **kwargs)
        raise exceptions.PermissionDenied

    def list(self, request, *args, **kwargs):
        if 'list' in self.allow_actions:
            return super(PermMethodViewSet, self).list(request, *args, **kwargs)
        raise exceptions.PermissionDenied

    def retrieve(self, request, *args, **kwargs):
        if 'retrieve' in self.allow_actions:
            return super(PermMethodViewSet, self).retrieve(request, *args, **kwargs)
        raise exceptions.PermissionDenied

    def update(self, request, *args, **kwargs):
        if 'update' in self.allow_actions:
            return super(PermMethodViewSet, self).update(request, *args, **kwargs)
        raise exceptions.PermissionDenied

    def destroy(self, request, *args, **kwargs):
        if 'destroy' in self.allow_actions:
            return super(PermMethodViewSet, self).destroy(request, *args, **kwargs)
        raise exceptions.PermissionDenied


class BaseViewSet(
    self_mixins.ConfirmModelMixin,
    self_mixins.LockModelMixin,
    self_mixins.ActiveModelMixin,
    self_mixins.DeleteModelMixin,
    PermMethodViewSet
):
    pass

class DataViewSet(BaseViewSet):
    pass

class OrderViewSet(
    self_mixins.DoneModelMixin,
    self_mixins.CancelModelMixin,
    BaseViewSet
):
    pass

class AuditOrderViewSet(
    self_mixins.AuditModelMixin,
    self_mixins.RejectModelMixin,
    self_mixins.AllowedModelMixin,
    OrderViewSet
):
    pass