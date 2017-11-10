#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
@author:    olinex
@time:      2017/11/9 下午9:28
"""

__all__ = ['ProfileViewSet']

from django.utils.translation import ugettext_lazy as _
from rest_framework.decorators import list_route
from rest_framework.response import Response
from django_perm.utils import view_perm_required

from common.rest.viewsets import PermMethodViewSet
from .. import models
from .. import serializers


class ProfileViewSet(PermMethodViewSet):
    def get_queryset(self):
        if self.request.user.is_superuser:
            return models.Profile.objects.all().order_by('-pk')
        return models.Profile.objects.filter(user=self.request.user)

    model = models.Profile
    allow_actions = ('create', 'list', 'retrieve', 'update')
    serializer_class = serializers.ProfileSerializer

    @list_route(['post'], serializer_class=serializers.MailNoticeSerializer)
    @view_perm_required
    def mail_notice(self, request):
        serializer = self.get_serializer(
            instance=request.user.profile,
            data=request.data
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {'detail': _('mail notice status changed successfully')},
        )

    @list_route(['post'], serializer_class=serializers.OnlineNoticeSerializer)
    @view_perm_required
    def online_notice(self, request):
        serializer = self.get_serializer(
            instance=request.user.profile,
            data=request.data
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {'detail': _('online notice status changed successfully')},
        )
