#!/usr/bin/env python3
#-*- coding:utf-8 -*-

from djangoperm.db import models

class QuantityField(models.DecimalField):
    '''数量单位'''
    def __init__(self,*args,uom,**kwargs):
        self.uom=uom
        kwargs['max_digits']=kwargs.get('max_digits') or 24
        kwargs['decimal_places']=kwargs.get('decimal_places') or 12
        super(QuantityField,self).__init__(*args,**kwargs)

    def deconstruct(self):
        name,path,args,kwargs = super(QuantityField,self).deconstruct()
        kwargs['uom'] = self.uom
        return name,path,args,kwargs

def floor_value(instance,field_name):
    '''
    获取实例指定字段通过单位转换精度的值
    :param instance: 数据表实例
    :param field: 字段名
    :return: decimal
    '''
    uom_name=instance.model._meta.fields[field_name].uom
    uom=getattr(instance,uom_name)
    return uom.floor_value(getattr(instance,field_name))

def uom_format_value(instance,field,uom_name):
    '''
    获取实例指定字段进行单位转换后的值
    :param instance: 数据表实例
    :param field: 字段名
    :param uom: 单位
    :return: decimal
    '''
    return instance.get(field)

