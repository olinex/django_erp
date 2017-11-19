#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
@author:    olinex
@time:      2017/11/18 下午10:09
"""

__all__ = ['MessageModelMixin']

from .. import serializers
from rest_framework.decorators import detail_route
from rest_framework.response import Response
from django_erp.rest.serializers import NoneSerializer
from django.utils.translation import ugettext_lazy as _


class MessageModelMixin(object):
    """
    contain the method for message
    """

    @detail_route(['get'], serializer_class=serializers.MessageSerializer)
    def message(self, request, pk=None):
        instance = getattr(self, 'get_object')()
        serializer = getattr(self, 'get_serializer')(instance=instance.messages, many=True)
        return Response(
            data=serializer.data
        )

    @detail_route(['post'], serializer_class=serializers.MessageSerializer)
    def create_message(self, request, pk=None):
        serializer = getattr(self, 'get_serializer')(data=request.data)
        if serializer.is_valid(raise_exception=True):
            instance = getattr(self, 'get_object')()
            instance.create_message(
                title=serializer.validated_data.get('title'),
                text=serializer.validated_data.get('text'),
                creater=request.user
            )
            return Response({'detail': _('create message success')})

    @detail_route(['patch'], serializer_class=NoneSerializer)
    def add_follower(self, request, pk=None):
        instance = getattr(self, 'get_object')()
        instance.add_followers(request.user)
        return Response({
            'detail': _('follow this {} success').format(instance)
        })

    @detail_route(['patch'], serializer_class=NoneSerializer)
    def remove_follower(self, request, pk=None):
        instance = getattr(self, 'get_object')()
        instance.remove_followers(request.user)
        return Response({
            'detail': _('unfollow this {} success').format(instance)
        })
