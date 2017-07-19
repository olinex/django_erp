#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from . import models
from django.contrib import admin
from product.admin import LotInline
from common.admin import CommonAdmin, CommonTabInLine


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

class ProcurementFromLocationSettingInline(CommonTabInLine):
    model = models.ProcurementFromLocationSetting
    fieldsets = (
        (None, {'fields': (
            'detail', 'location', 'quantity', 'route'
        )}),
    )

class RoutePathSortSettingInline(CommonTabInLine):
    model = models.RoutePathSortSetting
    fieldsets = (
        (None, {'fields': (
            'route', 'path', 'sequence'
        )})
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
            'package_template', 'product', 'quantity'
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
        'to_move', 'procurement_detail_setting', 'quantity', 'state'
    )
    list_filter = ('state',)
    list_editable = list_filter
    fieldsets = (
        (None, {'fields': (
            ('initial_location', 'end_location'),
            ('from_location', 'to_location'),
            'to_move', 'procurement_detail_setting',
            'quantity', 'state'
        )}),
    )


@admin.register(models.Path)
class PathAdmin(CommonAdmin):
    list_display = ('from_location', 'to_location')
    list_filter = list_display
    fieldsets = (
        (None, {'fields': ('from_location', 'to_location')}),
    )


@admin.register(models.Route)
class RouteAdmin(CommonAdmin):
    list_display = ('name', 'warehouse', 'direct_path', 'return_method', 'sequence')
    list_filter = ('return_method','warehouse')
    list_editable = ('name', 'return_method', 'sequence')
    search_fields = ('name',)
    fieldsets = (
        (None, {'fields': (
            'name', 'warehouse', 'direct_path',
            ('return_route', 'return_method'), 'sequence'
        )}),
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
    list_display = ('id','name', 'parent_node', 'template', 'quantity')
    list_editable = ('name', 'quantity')
    search_fields = ('name',)
    fieldsets = (
        (None, {'fields': ('name', 'quantity', ('parent_node', 'template'))}),
    )

@admin.register(models.Procurement)
class ProcurementAdmin(CommonAdmin):
    list_display = ('to_location','user','state')
    list_filter = ('state',)
    list_editable = list_filter
    fieldsets = (
        (None, {'fields': ('to_location', 'user', 'state')}),
    )

@admin.register(models.ProcurementDetail)
class ProcurementDetailAdmin(CommonAdmin):
    list_display = ('procurement','product','lot')
    fieldsets = (
        (None, {'fields': ('procurement', 'product', 'lot')}),
    )
    inlines = (
        ProcurementFromLocationSettingInline,
    )
