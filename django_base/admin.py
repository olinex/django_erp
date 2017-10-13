#!/usr/bin/env python3
#-*- coding:utf-8 -*-

from . import models
from common.admin import CommonTabInLine

from django.contrib import admin

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
    list_display_links = ('name',)
    search_fields = ('name',)
    list_editable = ('country',)
    fieldsets = (
        (None, {'fields': ('country', 'name')}),
    )
    inlines = [
        CityInline
    ]


@admin.register(models.City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('id', 'province', 'name')
    list_display_links = ('name',)
    search_fields = ('name',)
    list_editable = ('province',)
    fieldsets = (
        (None, {'fields': ('province', 'name')}),
    )
    inlines = (
        RegionInline,
    )


@admin.register(models.Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ('id', 'city', 'name')
    list_display_links = ('name',)
    search_fields = ('name',)
    list_editable = ('city',)
    fieldsets = (
        (None, {'fields': ('city', 'name')}),
    )
    inlines = (
        AddressInline,
    )
