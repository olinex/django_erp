#!/usr/bin/env python3
# -*- coding:utf-8 -*-

__all__ = ['ViewAccess']

from rest_framework import permissions
from django_perm.utils import has_view_perm
from django.utils.translation import ugettext_lazy as _


class ViewAccess(permissions.BasePermission):
    message = _('view permission deny')

    def has_permission(self, request, view):
        return has_view_perm(request)
