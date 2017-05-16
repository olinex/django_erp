#!/usr/bin/env python3
#-*- coding:utf-8 -*-

from . import models
from . import serializers
from common.rest import mixin
from django.shortcuts import render
from djangoperm.utils import view_perm_required
from rest_framework import viewsets,status,permissions
from rest_framework.response import Response
from rest_framework.decorators import list_route,detail_route,api_view,permission_classes

def first_request(request):
    return render(request,'index.html')

class UserViewSet(mixin.IsActiveModelMixin,mixin.PermMethodViewSet):
    allow_actions = ('update','list','retrieve','create','destroy')
    serializer_class = serializers.UserSerializer

    def get_queryset(self):
        from django.contrib.auth.models import User
        if self.request.user.is_superuser:
            return User.objects.all()
        return User.objects.filter(pk=self.request.user.id)

    @list_route(['get'])
    def myself(self,request):
        '''
        获取用户当前自身的数据
        '''
        return Response(self.get_serializer(instance=request.user).data)

    @list_route(
        ['post'],
        permission_classes=[permissions.AllowAny],
        serializer_class=serializers.LoginSerializer
    )
    def login(self,request):
        '''
        通过ajax登录
        '''
        from django.contrib.auth import login
        from django.contrib.auth.forms import AuthenticationForm
        form=AuthenticationForm(request,request.data)
        if form.is_valid():
            user=form.user_cache
            login(request,user)
            return Response(serializers.UserSerializer(instance=user).data)
        return Response(
            {'detail':'认证未通过'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    @list_route(['get'],serializer_class=None)
    def logout(self,request):
        '''
        通过ajax登出
        :param request: 
        :return: 
        '''
        from django.contrib.auth import logout
        logout(request)
        return Response({'detail':'成功登出'})

    @detail_route(
        ['post'],
        serializer_class=serializers.ResetPasswordSerializer
    )
    @view_perm_required
    def password(self,request,pk=None):
        instance=self.get_object()
        serializer=self.get_serializer(
            instance=instance,
            data=request.data
        )
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(
                {'detail':'密码修改成功'},
                status=status.HTTP_202_ACCEPTED
            )
        return Response(
            {'detail':'验证错误'},
            status=status.HTTP_403_FORBIDDEN
        )

