#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from django.contrib import admin
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _

def active(modeladmin,request,queryset):
    if queryset.filter(is_delete=True).exists():
        modeladmin.message_user(
            request,
            _('Deleted rows was selected'),
            level=messages.ERROR,
        )
    else:
        queryset.update(is_active=True)
        modeladmin.message_user(request,_('act rows successfully'))
active.short_description=_('active')

def lock(modeladmin,request,queryset):
    if queryset.filter(is_delete=True).exists():
        modeladmin.message_user(
            request,
            _('Deleted rows was selected'),
            level=messages.ERROR,
        )
    else:
        queryset.update(is_active=False)
        modeladmin.message_user(request,_('lock rows successfully'))
lock.short_description=_('lock')

def delete(modeladmin,request,queryset):
    if queryset.filter(is_active=False).exists():
        modeladmin.message_user(
            request,
            _('locked rows was selected'),
            level=messages.ERROR,
        )
    else:
        queryset.update(is_delete=True)
        modeladmin.message_user(request,'delete rows successfully')
delete.short_description=_('delete')

class CommonAdmin(admin.ModelAdmin):
    LIST_DISPLAY = (
        'is_active',
        'is_delete',
        'create_time',
        'last_modify_time',
    )

    LIST_FILTER = (
        'is_active',
        'is_delete',
    )

    READONLY_FIELDS = (
        'is_delete',
        'create_time',
        'last_modify_time',
    )

    def get_list_display(self, request):
        return (
            super(CommonAdmin,self).get_list_display(request) +
            self.LIST_DISPLAY
        )

    def get_list_filter(self, request):
        return (
            super(CommonAdmin,self).get_list_filter(request) +
            self.LIST_FILTER
        )

    def get_readonly_fields(self, request, obj=None):
        return (
            super(CommonAdmin,self).get_readonly_fields(request,obj) +
            self.READONLY_FIELDS
        )

    list_display_links = ('id',)
    list_per_page = 20
    empty_value_display = _('- empty -')
    actions = [active,lock,delete]
    save_as = True
    save_on_top = True

    def delete_model(self, request, obj):
        if hasattr(obj,'is_delete') and obj.is_delete is False:
            obj.is_delete=True
            obj.save()

class CommonTabInLine(admin.TabularInline):
    list_display = CommonAdmin.LIST_DISPLAY
