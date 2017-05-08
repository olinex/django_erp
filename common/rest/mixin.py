#!/usr/bin/env python3
#-*- coding:utf-8 -*-

'''
Created on 2016年9月4日

@author: olin
'''
import json
from rest_framework import mixins,exceptions,viewsets

class IsDeleteModelMixin(mixins.DestroyModelMixin):
    '''将删除改为修改delStatus状态'''
    def perform_destroy(self, instance):
        '''删除对象'''
        instance.is_delete=True
        instance.save(update_fields=('is_delete',))
        
class IsActiveModelMixin(mixins.DestroyModelMixin):
    '''将删除改为修改isActive状态'''
    def perform_destroy(self, instance):
        '''删除对象'''
        instance.is_active=False
        instance.save(update_fields=('is_active',))

class PermMethodViewSet(
        mixins.CreateModelMixin,
        mixins.ListModelMixin,
        mixins.RetrieveModelMixin,
        mixins.UpdateModelMixin,
        mixins.DestroyModelMixin,
        viewsets.GenericViewSet):
    '''http请求方法级别权限'''
    allow_actions = ('create','list','retrieve','update','destory')
    def method_permission(self,request,*args,**kwargs):
        return True
    
    def create(self,request,*args,**kwargs):
        if (('create' in self.allow_actions) and
        getattr(self,'create_permission',self.method_permission)(request,*args,**kwargs)):
            return super(PermMethodViewSet,self).create(request,*args,**kwargs)
        raise exceptions.PermissionDenied
    
    def list(self,request,*args,**kwargs):
        if (('list' in self.allow_actions) and
        getattr(self,'list_permission',self.method_permission)(request,*args,**kwargs)):
            return super(PermMethodViewSet,self).list(request,*args,**kwargs)
        raise exceptions.PermissionDenied
    
    def retrieve(self,request,*args,**kwargs):
        if (('retrieve' in self.allow_actions) and
        getattr(self,'retrieve_permission',self.method_permission)(request,*args,**kwargs)):
            return super(PermMethodViewSet,self).retrieve(request,*args,**kwargs)
        raise exceptions.PermissionDenied
    
    def update(self,request,*args,**kwargs):
        if (('update' in self.allow_actions) and
        getattr(self,'update_permission',self.method_permission)(request,*args,**kwargs)):
            return super(PermMethodViewSet,self).update(request,*args,**kwargs)
        raise exceptions.PermissionDenied
        
    def destroy(self,request,*args,**kwargs):
        if (('destroy' in self.allow_actions) and
        getattr(self,'destroy_permission',self.method_permission)(request,*args,**kwargs)):
            return super(PermMethodViewSet,self).destroy(request,*args,**kwargs)
        raise exceptions.PermissionDenied