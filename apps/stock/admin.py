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
            'from_location', 'to_location',
            'to_move', 'procurement_detail',
            'route_setting', 'quantity', 'state'
        )}),
    )


class RouteSettingInline(CommonTabInLine):
    model = models.RouteSetting
    fieldsets = (
        (None, {'fields': (
            'route', 'location', 'sequence'
        )}),
    )


class PackageTypeSettingInline(CommonTabInLine):
    model = models.PackageTypeSetting
    fieldsets = (
        (None, {'fields': (
            'package_type', 'item', 'max_quantity'
        )}),
    )


class PackageTemplateSettingInline(CommonTabInLine):
    model = models.PackageTemplateSetting
    fieldsets = (
        (None, {'fields': (
            'package_template', 'type_setting', 'quantity'
        )}),
    )


@admin.register(models.Warehouse)
class WarehouseAdmin(CommonAdmin):
    list_display = ('name', 'manager', 'address')
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
        'from_location', 'to_location',
        'quantity', 'state'
    )
    list_filter = ('state',)
    list_editable = list_filter
    fieldsets = (
        (None, {'fields': (
            ('from_location', 'to_location'),
            'to_move',
            'quantity', 'state'
        )}),
    )


@admin.register(models.Route)
class RouteAdmin(CommonAdmin):
    list_display = ('name', 'warehouse', 'route_type', 'sequence')
    list_filter = ('warehouse',)
    list_editable = ('name', 'sequence')
    search_fields = ('name',)
    fieldsets = (
        (None, {'fields': (
            'name', 'warehouse', 'route_type', 'sequence'
        )}),
    )
    inlines = (
        RouteSettingInline,
    )


@admin.register(models.PackageType)
class PackageTypeAdmin(CommonAdmin):
    search_fields = list_editable = list_display = ('name',)
    fieldsets = (
        (None, {'fields': ('name',)}),
    )
    inlines = (
        PackageTypeSettingInline,
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
        PackageTemplateSettingInline,
    )


@admin.register(models.PackageNode)
class PackageNodeAdmin(admin.ModelAdmin):
    list_display = ('id', 'parent_node', 'template')
    fieldsets = (
        (None, {'fields': ('parent_node', 'template')}),
    )


@admin.register(models.Procurement)
class ProcurementAdmin(CommonAdmin):
    list_display = ('user', 'state')
    list_filter = ('state',)
    list_editable = list_filter
    fieldsets = (
        (None, {'fields': ('user', 'state')}),
    )


@admin.register(models.ProcurementDetail)
class ProcurementDetailAdmin(CommonAdmin):
    list_display = ('procurement', 'item', 'quantity', 'direct_return', 'route')
    list_filter = ('direct_return',)
    fieldsets = (
        (None, {'fields': ('procurement', 'direct_return', 'route', ('item', 'quantity'))}),
    )
