#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
@author:    olinex
@time:      2017/11/17 下午11:02
"""

__all__ = ['MessageViewSet']

from .. import models, serializers, filters
from rest_framework.decorators import list_route, detail_route
from rest_framework.response import Response
from django_erp.rest.viewsets import PermMethodViewSet
from django_erp.rest.serializers import NoneSerializer
from django.utils.translation import ugettext_lazy as _


class MessageViewSet(PermMethodViewSet):
    model = models.Message
    allow_actions = ('list', 'retrieve')
    serializer_class = serializers.MessageSerializer
    filter_class = filters.MessageFilter

    def get_queryset(self):
        return self.model.objects.select_related('creater').all()

    @list_route(['get'])
    def new(self,request):
        serializer = self.get_serializer(
            instance=request.user.new_messages,
            many=True
        )
        return Response(
            data=serializer.data
        )

    @detail_route(['patch'],serializer_class=NoneSerializer)
    def remove(self,requrest, pk=None):
        requrest.user.remove_message(pk=pk)
        return Response({'detail': _('message remove successfully')})

    @list_route(['patch'], serializer_class=NoneSerializer)
    def clear(self, requrest):
        requrest.user.clear_messages()
        return Response({'detail': _('message clear successfully')})


