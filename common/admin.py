#!/usr/bin/env python3
#-*- coding:utf-8 -*-

from django.contrib import admin
from django.contrib import messages

def active(modeladmin,request,queryset):
    if queryset.filter(is_delete=True).exists():
        modeladmin.message_user(
            request,
            '选中存在已删除记录',
            level=messages.ERROR,
        )
    else:
        queryset.update(is_active=True)
        modeladmin.message_user(request,'解锁成功')
active.short_description="解锁"

def lock(modeladmin,request,queryset):
    if queryset.filter(is_delete=True).exists():
        modeladmin.message_user(
            request,
            '选中存在已删除记录',
            level=messages.ERROR,
        )
    else:
        queryset.update(is_active=False)
        modeladmin.message_user(request,'锁定成功')
lock.short_description="锁定"

def delete(modeladmin,request,queryset):
    if queryset.filter(is_active=False).exists():
        modeladmin.message_user(
            request,
            '选中存在已锁定记录',
            level=messages.ERROR,
        )
    else:
        queryset.update(is_delete=True)
        modeladmin.message_user(request,'删除成功')
delete.short_description="删除"

class CommonAdmin(admin.ModelAdmin):
    list_per_page = 20
    empty_value_display = '- empty -'
    actions = [active,lock,delete]
