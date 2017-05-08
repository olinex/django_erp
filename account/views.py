#!/usr/bin/env python3
#-*- coding:utf-8 -*-

from . import models
from . import serializers
from common.rest import mixin
from django.shortcuts import render
from rest_framework import viewsets,status,permissions
from rest_framework.response import Response
from rest_framework.decorators import list_route,detail_route,api_view,permission_classes

def first_request(request):
    return render(request,'index.html')

class UserViewSet(mixin.PermMethodViewSet):
    allow_actions = ('retrieve','update')
    serializer_class = serializers.UserSerializer

    def get_queryset(self):
        '''
        仅允许获取当前用户自身
        '''
        from django.contrib.auth.models import User
        return User.objects.filter(pk=self.request.user.id)

    @list_route(
        ['post'],
        permission_classes=[permissions.AllowAny],
        serializer_class=serializers.LoginSerializer,
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
            serializer=serializers.UserSerializer(instance=user)
            return Response(serializer.data)
        return Response({'detail':'认证未通过'},status=status.HTTP_401_UNAUTHORIZED)

    @list_route(
        ['get'],
        permission_classes=[permissions.IsAuthenticated],
        serializer_class=None
    )
    def logout(self,request):
        '''
        通过ajax登出
        :param request: 
        :return: 
        '''
        from django.contrib.auth import logout
        logout(request)
        return Response({'detail':'成功登出'})
