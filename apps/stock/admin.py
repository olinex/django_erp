#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from django.contrib import admin

from common.admin import CommonAdmin, CommonTabInLine
from . import models


class ZoneInline(CommonTabInLine):
    model = models.Zone
    fieldsets = (
        (None, {'fields': ('usage',)}),
    )


class LocationInline(CommonTabInLine):
    model = models.Location
    fieldsets = (
        (None, {'fields': ('zone', 'parent_location', 'is_virtual', 'x', 'y', 'z')}),
    )


class MoveInline(CommonTabInLine):
    model = models.Move
    fieldsets = (
        (None, {'fields': (
            'initial_location', 'end_location', 'from_location', 'to_location',
            'to_move', 'procurement_detail_setting', 'quantity', 'state'
        )}),
    )


class RouteLocationSettingInline(CommonTabInLine):
    model = models.RouteLocationSetting
    fieldsets = (
        (None, {'fields': (
            'route', 'location', 'sequence'
        )}),
    )


class PackageTypeProductSettingInline(CommonTabInLine):
    model = models.PackageTypeProductSetting
    fieldsets = (
        (None, {'fields': (
            'package_type', 'product', 'max_quantity'
        )}),
    )


class PackageTemplateProductSettingInline(CommonTabInLine):
    model = models.PackageTemplateProductSetting
    fieldsets = (
        (None, {'fields': (
            'package_template', 'type_setting', 'quantity'
        )}),
    )


@admin.register(models.Warehouse)
class WarehouseAdmin(CommonAdmin):
    list_display = ('name', 'user', 'address')
    search_fields = ('name',)
    list_editable = ('name',)
    inlines = (
        ZoneInline,
    )


@admin.register(models.Zone)
class ZoneAdmin(CommonAdmin):
    list_display = ('warehouse', 'usage')
    list_filter = list_display
    list_editable = ('usage',)
    inlines = (
        LocationInline,
    )


@admin.register(models.Location)
class LocationAdmin(CommonAdmin):
    list_display = ('zone', 'parent_node', 'is_virtual', 'x', 'y', 'z')
    list_filter = ('is_virtual',)
    search_fields = ('x', 'y', 'z')
    list_editable = search_fields
    fieldsets = (
        (None, {'fields': (
            ('zone', 'parent_node'),
            'is_virtual', ('x', 'y', 'z')
        )}),
    )


@admin.register(models.Move)
class MoveAdmin(CommonAdmin):
    list_display = (
        'initial_location', 'end_location', 'from_location', 'to_location',
        'to_move', 'procurement_detail', 'route_location_setting', 'quantity', 'state'
    )
    list_filter = ('state',)
    list_editable = list_filter
    fieldsets = (
        (None, {'fields': (
            ('initial_location', 'end_location'),
            ('from_location', 'to_location'),
            'to_move', 'procurement_detail',
            'route_location_setting', 'quantity', 'state'
        )}),
    )


@admin.register(models.Route)
class RouteAdmin(CommonAdmin):
    list_display = ('name', 'warehouse', 'sequence')
    list_filter = ('warehouse',)
    list_editable = ('name', 'sequence')
    search_fields = ('name',)
    fieldsets = (
        (None, {'fields': (
            'name', 'warehouse', 'sequence'
        )}),
    )
    inlines = (
        RouteLocationSettingInline,
    )


@admin.register(models.PackageType)
class PackageTypeAdmin(CommonAdmin):
    search_fields = list_editable = list_display = ('name',)
    fieldsets = (
        (None, {'fields': ('name',)}),
    )
    inlines = (
        PackageTypeProductSettingInline,
    )


@admin.register(models.PackageTemplate)
class PackageTemplateAdmin(CommonAdmin):
    list_display = ('name', 'package_type')
    list_filter = ('package_type',)
    list_editable = ('name',)
    search_fields = list_editable
    fieldsets = (
        (None, {'fields': ('name', 'package_type')}),
    )
    inlines = (
        PackageTemplateProductSettingInline,
    )


@admin.register(models.PackageNode)
class PackageNodeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'parent_node', 'template', 'quantity')
    list_editable = ('name', 'quantity')
    search_fields = ('name',)
    fieldsets = (
        (None, {'fields': ('name', 'quantity', ('parent_node', 'template'))}),
    )


@admin.register(models.Procurement)
class ProcurementAdmin(CommonAdmin):
    list_display = ('to_location', 'user', 'is_return', 'return_procurement', 'state')
    list_filter = ('state', 'is_return')
    list_editable = list_filter
    fieldsets = (
        (None, {'fields': ('to_location', 'user', 'is_return', 'return_procurement', 'state')}),
    )


@admin.register(models.ProcurementDetail)
class ProcurementDetailAdmin(CommonAdmin):
    list_display = ('procurement', 'product', 'route', 'quantity', 'lot')
    fieldsets = (
        (None, {'fields': (('procurement', 'route'), ('product', 'quantity'), 'lot')}),
    )
