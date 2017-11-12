#!/usr/bin/env python3
# -*- coding:utf-8 -*-

__all__ = [
    'CommonTabInLine',
    'CommonAdmin',
    'active',
    'lock',
    'confirm',
    'delete'
]

from django.contrib import admin
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _


def active(modeladmin, request, queryset):
    if queryset.filter(is_draft=True).exists():
        modeladmin.message_user(
            request,
            _('draft rows was selected'),
            level=messages.ERROR,
        )
    else:
        queryset.update(is_active=True)
        modeladmin.message_user(
            request,
            _('turn rows to active status successfully')
        )


active.short_description = _('active')


def lock(modeladmin, request, queryset):
    if queryset.filter(is_draft=True).exists():
        modeladmin.message_user(
            request,
            _('draft rows was selected'),
            level=messages.ERROR,
        )
    else:
        queryset.update(is_active=False)
        modeladmin.message_user(
            request,
            _('turn rows to lock status successfully')
        )


lock.short_description = _('lock')

def confirm(modeladmin, request, queryset):
    if queryset.filter(is_draft=False).exist():
        modeladmin.message_user(
            request,
            _('confirm rows was selected'),
            level=messages.ERROR,
        )
    else:
        queryset.update(is_draft=False)
        modeladmin.message_user(
            request,
            _('turn rows to lock status successfully')
        )

confirm.short_description = _('confirm')

def delete(modeladmin, request, queryset):
    if queryset.filter(is_draft=False).exists():
        modeladmin.message_user(
            request,
            _('confirmed rows was selected'),
            level=messages.ERROR,
        )
    else:
        queryset.delete()
        modeladmin.message_user(
            request,
            _('delete successfully')
        )


delete.short_description = _('delete')


class CommonAdmin(admin.ModelAdmin):
    LIST_DISPLAY = (
        'is_active',
        'is_draft',
        'create_time',
        'last_modify_time',
    )

    LIST_FILTER = (
        'is_active',
        'is_draft',
    )

    READONLY_FIELDS = (
        'is_active',
        'is_draft',
        'create_time',
        'last_modify_time',
    )
    readonly_fields = (
        'is_active',
        'is_draft',
        'create_time',
        'last_modify_time',
    )

    def get_list_display(self, request):
        return (
            super(CommonAdmin, self).get_list_display(request) +
            self.LIST_DISPLAY
        )

    def get_list_filter(self, request):
        return (
            super(CommonAdmin, self).get_list_filter(request) +
            self.LIST_FILTER
        )

    def get_readonly_fields(self, request, obj=None):
        return (
            super(CommonAdmin, self).get_readonly_fields(request, obj) +
            self.READONLY_FIELDS
        )

    list_display_links = ('id',)
    list_per_page = 20
    empty_value_display = _('- empty -')
    actions = [active, lock, confirm, delete]
    save_as = True
    save_on_top = True

    def delete_model(self, request, obj):
        if obj.is_draft:
            obj.delete()


class CommonTabInLine(admin.TabularInline):
    list_display = CommonAdmin.LIST_DISPLAY
