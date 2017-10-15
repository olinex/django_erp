#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from .mixin import IsActiveModelMixin,IsDeleteModelMixin
from rest_framework import mixins,exceptions,viewsets
from django_perm.utils import has_view_perm

class PermMethodViewSet(
        mixins.CreateModelMixin,
        mixins.ListModelMixin,
        mixins.RetrieveModelMixin,
        mixins.UpdateModelMixin,
        mixins.DestroyModelMixin,
        viewsets.GenericViewSet):
    '''http请求方法级别权限'''
    allow_actions = ('create','list','retrieve','update','destroy')

    def get_queryset(self):
        return self.queryset if self.queryset else self.model.objects.all()


    def create(self,request,*args,**kwargs):
        if 'create' in self.allow_actions and has_view_perm(request):
            return super(PermMethodViewSet,self).create(request,*args,**kwargs)
        raise exceptions.PermissionDenied

    def list(self,request,*args,**kwargs):
        if 'list' in self.allow_actions and has_view_perm(request):
            return super(PermMethodViewSet,self).list(request,*args,**kwargs)
        raise exceptions.PermissionDenied

    def retrieve(self,request,*args,**kwargs):
        if 'retrieve' in self.allow_actions and has_view_perm(request):
            return super(PermMethodViewSet,self).retrieve(request,*args,**kwargs)
        raise exceptions.PermissionDenied

    def update(self,request,*args,**kwargs):
        if 'update' in self.allow_actions and has_view_perm(request):
            return super(PermMethodViewSet,self).update(request,*args,**kwargs)
        raise exceptions.PermissionDenied

    def destroy(self,request,*args,**kwargs):
        if 'destroy' in self.allow_actions and has_view_perm(request):
            return super(PermMethodViewSet,self).destroy(request,*args,**kwargs)
        raise exceptions.PermissionDenied


class ActiveBaseViewSet(IsActiveModelMixin,PermMethodViewSet):
    def get_queryset(self):
        return super(ActiveBaseViewSet,self).get_queryset().filter(is_delete=False)

class DeleteBaseViewSet(IsDeleteModelMixin,PermMethodViewSet):
    pass

class BaseViewSet(ActiveBaseViewSet,DeleteBaseViewSet):
    pass

