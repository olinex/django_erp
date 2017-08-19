#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from django.contrib import admin

from common.admin import CommonAdmin, CommonTabInLine
from . import models


class CityInline(admin.TabularInline):
    model = models.City
    fieldsets = (
        (None, {'fields': ('name',)}),
    )


class RegionInline(admin.TabularInline):
    model = models.Region
    fieldsets = (
        (None, {'fields': ('name',)}),
    )


class AddressInline(CommonTabInLine):
    model = models.Address
    fieldsets = (
        (None, {'fields': ('name', 'is_active', 'is_delete')}),
    )


@admin.register(models.Province)
class ProvinceAdmin(admin.ModelAdmin):
    list_display = ('id', 'country', 'name')
    search_fields = ('name',)
    list_editable = ('name',)
    fieldsets = (
        (None, {'fields': ('country', 'name')}),
    )
    inlines = [
        CityInline
    ]


@admin.register(models.City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('id', 'province', 'name')
    search_fields = ('name',)
    list_editable = ('name',)
    fieldsets = (
        (None, {'fields': ('province', 'name')}),
    )
    inlines = (
        RegionInline,
    )


@admin.register(models.Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ('id', 'city', 'name')
    search_fields = ('name',)
    list_editable = ('name',)
    fieldsets = (
        (None, {'fields': ('city', 'name')}),
    )
    inlines = (
        AddressInline,
    )

@admin.register(models.Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'tel', 'address', 'salable', 'purchasable')
    list_display_links = ('id',)
    list_filter = ('salable', 'purchasable')
    search_fields = ('name', 'tel', 'address__name')
    list_editable = ('name', 'tel', 'salable', 'purchasable')
    fieldsets = (
        (None, {'fields': (
            'name', 'tel', 'address',
            'default_send_address',
            'usual_send_addresses',
            'is_active',
            'belong_users',
            ('salable', 'purchasable'),
        )}),
    )

@admin.register(models.Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'sex', 'phone', 'online_notice', 'mail_notice', 'language',
        'address', 'default_send_address', 'is_partner', 'purchasable', 'salable'
    )
    list_filter = (
        'sex', 'online_notice', 'mail_notice', 'is_partner', 'purchasable', 'salable'
    )
    search_fields = ('phone', 'user__username')
    list_per_page = 20
    list_editable = (
        'phone', 'sex', 'online_notice', 'mail_notice',
        'language', 'is_partner', 'purchasable', 'salable'
    )
    fieldsets = (
        (None, {'fields': (
            'user', 'sex', 'phone', 'language', ('online_notice', 'mail_notice'),
            'address','default_send_address','usual_send_addresses',
            ('salable','purchasable','is_partner')
        )}),
    )