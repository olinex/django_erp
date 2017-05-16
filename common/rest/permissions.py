#!/usr/bin/env python3
#-*- coding:utf-8 -*-

from djangoperm.utils import has_view_perm
from rest_framework import permissions

class ViewAccess(permissions.BasePermission):
    message='Access is not allowwd'

    def has_permission(self, request, view):
        return has_view_perm(request)