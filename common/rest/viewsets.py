#!/usr/bin/env python3
#-*- coding:utf-8 -*-

from .mixin import IsActiveModelMixin,IsDeleteModelMixin
from rest_framework import mixins,exceptions,viewsets


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
        queryset=self.queryset if self.queryset else self.model.objects.all()
        return queryset.filter(is_delete=False)

    def create(self,request,*args,**kwargs):
        if 'create' in self.allow_actions:
            return super(PermMethodViewSet,self).create(request,*args,**kwargs)
        raise exceptions.PermissionDenied

    def list(self,request,*args,**kwargs):
        if 'list' in self.allow_actions:
            return super(PermMethodViewSet,self).list(request,*args,**kwargs)
        raise exceptions.PermissionDenied

    def retrieve(self,request,*args,**kwargs):
        if 'retrieve' in self.allow_actions:
            return super(PermMethodViewSet,self).retrieve(request,*args,**kwargs)
        raise exceptions.PermissionDenied

    def update(self,request,*args,**kwargs):
        if 'update' in self.allow_actions:
            return super(PermMethodViewSet,self).update(request,*args,**kwargs)
        raise exceptions.PermissionDenied

    def destroy(self,request,*args,**kwargs):
        if 'destroy' in self.allow_actions:
            return super(PermMethodViewSet,self).destroy(request,*args,**kwargs)
        raise exceptions.PermissionDenied

class ActiveBaseViewSet(IsActiveModelMixin,PermMethodViewSet):
    pass

class DeleteBaseViewSet(IsDeleteModelMixin,PermMethodViewSet):
    pass

class BaseViewSet(ActiveBaseViewSet,DeleteBaseViewSet):
    pass

