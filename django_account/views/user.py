#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
@author:    olinex
@time:      2017/11/9 下午8:54
"""

__all__ = [
    "UserViewSet",
]

from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _
from rest_framework import status, permissions
from rest_framework.decorators import list_route
from rest_framework.response import Response
from django_perm.utils import view_perm_required

from common.rest.viewsets import PermMethodViewSet
from .. import serializers
from .. import filters

User = get_user_model()


class UserViewSet(PermMethodViewSet):
    serializer_class = serializers.UserSerializer
    allow_actions = ('create', 'list', 'retrieve', 'update')
    filter_class = filters.UserFilter
    ordering_fields = ('id', 'username', 'first_name', 'last_name', 'email')

    def get_queryset(self):
        queryset = User.objects.select_related(
            'profile', 'profile__address',
            'profile__default_send_address'
        ).prefetch_related(
            'profile__usual_send_addresses'
        ).order_by('-pk')
        if self.request.user.is_superuser:
            return queryset.all().order_by('-pk')
        return queryset.filter(pk=self.request.user.id)

    @list_route(['get'])
    @view_perm_required
    def myself(self, request):
        """
        get user's self information
        """
        return Response(self.get_serializer(instance=request.user).data)

    @list_route(
        ['post'],
        permission_classes=[permissions.AllowAny],
        serializer_class=serializers.LoginSerializer
    )
    def login(self, request):
        """
        ajax login api
        """
        from django.contrib.auth import login
        from django.contrib.auth.forms import AuthenticationForm
        form = AuthenticationForm(request, request.data)
        if form.is_valid():
            user = form.user_cache
            login(request, user)
            return Response(serializers.UserSerializer(instance=user).data)
        return Response(
            {'detail': _('authentication failed')},
            status=status.HTTP_403_FORBIDDEN
        )

    @list_route(['get'], serializer_class=None)
    def logout(self, request):
        """
        logout through ajax
        """
        from django.contrib.auth import logout
        logout(request)
        return Response({'detail': _('logout successfully')})

    @list_route(['post'], serializer_class=serializers.ResetPasswordSerializer)
    @view_perm_required
    def password(self, request):
        serializer = self.get_serializer(
            instance=request.user,
            data=request.data
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {'detail': _('password changed successfully')},
        )
