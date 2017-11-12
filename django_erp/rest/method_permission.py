#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Created on 2017年1月7日

@author: joshu
"""

from rest_framework.compat import is_authenticated


def superuserMethod(viewset, request, *args, **kwargs):
    """only allow superuser to call"""
    return (
        request.user.is_superuser or
        request.auth.user.is_superuser
    )


def staffMethod(viewset, request, *args, **kwargs):
    """only allow staff user to call"""
    return (
        request.user.is_staff or
        request.auth.user.is_staff or
        superuserMethod(viewset, request, *args, **kwargs)
    )


def authenticatedMethod(viewset, request, *args, **kwargs):
    """only allow system user to call"""
    return (
        is_authenticated(request.user) or
        is_authenticated(request.auth.user) or
        superuserMethod(viewset, request, *args, **kwargs)
    )
