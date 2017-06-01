#!/usr/bin/env python3
#-*- coding:utf-8 -*-

'''
Created on 2016年9月4日

@author: olin
'''
import json
from common.rest.serializers import ActiveSerializer
from rest_framework.decorators import detail_route
from rest_framework import mixins,exceptions,viewsets

class IsDeleteModelMixin(mixins.DestroyModelMixin):
    '''将删除改为修改delStatus状态'''
    def perform_destroy(self, instance):
        '''删除对象'''
        instance.is_delete=True
        instance.save(update_fields=('is_delete',))
        
class IsActiveModelMixin(object):
    '''添加实例激活或锁定的方法'''
    @detail_route(['patch'],serializer_class=ActiveSerializer)
    def active(self,request,pk=None):
        instance=self.get_object()
        serializer=self.get_serializer(data=request.data)
        if serializer.is_vaild(raise_exception=True):
            instance.is_active=serializer.validated_data['is_active']
            instance.save()
