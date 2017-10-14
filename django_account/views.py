#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _
from rest_framework import status, permissions
from rest_framework.decorators import list_route
from rest_framework.response import Response
from django_perm.utils import view_perm_required

from common.rest.viewsets import BaseViewSet, PermMethodViewSet
from . import models
from . import serializers
from . import filters

User = get_user_model()


def first_request(request):
    return render(request, 'index.html')


class UserViewSet(PermMethodViewSet):
    serializer_class = serializers.UserSerializer
    allow_actions = ('create', 'list', 'retrieve', 'update')
    filter_class = filters.UserFilter
    ordering_fields = ('id','username','first_name','last_name','email')

    def get_queryset(self):
        if self.request.user.is_superuser:
            return User.objects.all()
        return User.objects.filter(pk=self.request.user.id).select_related(
            'profile','profile__address',
            'profile__default_send_address',
            'profile__usual_send_addresses'
        )

    @list_route(['get'])
    @view_perm_required
    def myself(self, request):
        '''
        get user's self information
        '''
        return Response(self.get_serializer(instance=request.user).data)

    @list_route(
        ['post'],
        permission_classes=[permissions.AllowAny],
        serializer_class=serializers.LoginSerializer
    )
    @view_perm_required
    def login(self, request):
        '''
        ajax login api
        '''
        from django.contrib.auth import login
        from django.contrib.auth.forms import AuthenticationForm
        form = AuthenticationForm(request, request.data)
        if form.is_valid():
            user = form.user_cache
            login(request, user)
            return Response(serializers.UserSerializer(instance=user).data)
        return Response(
            {'detail': _('authentication failed')},
            status=status.HTTP_401_UNAUTHORIZED
        )

    @list_route(['get'], serializer_class=None)
    @view_perm_required
    def logout(self, request):
        '''
        logout through ajax
        '''
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


class PartnerViewSet(BaseViewSet):
    model = models.Partner
    serializer_class = serializers.PartnerSerializer


class ProfileViewSet(PermMethodViewSet):
    def get_queryset(self):
        if self.request.user.is_superuser:
            return models.Profile.objects.all()
        return models.Profile.objects.filter(user=self.request.user)

    model = models.Profile
    allow_actions = ('create', 'list', 'retrieve', 'update')
    serializer_class = serializers.ProfileSerializer

    @list_route(['post'], serializer_class=serializers.MailNoticeSerializer)
    @view_perm_required
    def mail_notice(self, request):
        serializers = self.get_serializer(
            instance=request.user.profile,
            data=request.data
        )
        serializers.is_valid(raise_exception=True)
        serializers.save()
        return Response(
            {'detail': _('mail notice status changed successfully')},
        )

    @list_route(['post'], serializer_class=serializers.OnlineNoticeSerializer)
    @view_perm_required
    def online_notice(self, request):
        serializers = self.get_serializer(
            instance=request.user.profile,
            data=request.data
        )
        serializers.is_valid(raise_exception=True)
        serializers.save()
        return Response(
            {'detail': _('online notice status changed successfully')},
        )
