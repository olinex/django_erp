#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
@author:    olinex
@time:      2017/11/9 上午10:55
"""

from django.contrib import admin
from . import models


@admin.register(models.Partner)
class PartnerAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'phone', 'address', 'is_company', 'sale_able', 'purchase_able')
    list_display_links = ('name',)
    list_filter = ('is_company', 'sale_able', 'purchase_able')
    search_fields = ('name', 'phone', 'address__name')
    list_editable = ('phone', 'is_company', 'sale_able', 'purchase_able')
    fieldsets = (
        (None, {'fields': (
            'name', 'phone', 'address',
            'default_send_address',
            'usual_send_addresses',
            'is_active', 'managers',
            ('is_company', 'sale_able', 'purchase_able')
        )}),
    )


@admin.register(models.Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'sex', 'phone', 'online_notice', 'mail_notice', 'language',
        'address', 'default_send_address',
    )
    list_display_links = ('user',)
    list_filter = (
        'sex', 'online_notice', 'mail_notice'
    )
    search_fields = ('phone', 'user__username')
    list_editable = (
        'phone', 'sex', 'online_notice', 'mail_notice', 'language'
    )
    fieldsets = (
        (None, {'fields': (
            'user', 'sex', 'phone', 'language', ('online_notice', 'mail_notice'),
            'address', 'default_send_address', 'usual_send_addresses',
        )}),
    )
