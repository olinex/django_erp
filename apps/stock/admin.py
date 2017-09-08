#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from django.contrib import admin

from common.admin import CommonAdmin, CommonTabInLine
from . import models


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
        (None, {'fields': ('name', 'location', 'sequence')}),
    )


@admin.register(models.Warehouse)
class WarehouseAdmin(CommonAdmin):
    list_display = ('name', 'manager', 'address')
    search_fields = ('name',)
    list_editable = ('name',)
    inlines = (
        LocationInline,
    )



@admin.register(models.Location)
class LocationAdmin(CommonAdmin):
    list_display = ('zone', 'parent_node', 'is_virtual', 'x', 'y', 'z', 'index')
    list_filter = ('is_virtual',)
    search_fields = ('x', 'y', 'z')
    list_editable = ('is_virtual', 'x', 'y', 'z')
    fieldsets = (
        (None, {'fields': (
            ('zone', 'parent_node'),
            'is_virtual', ('x', 'y', 'z')
        )}),
    )


@admin.register(models.Move)
class MoveAdmin(CommonAdmin):
    list_display = (
        'from_location', 'to_location', 'to_move',
        'from_route_setting', 'to_route_setting', 'quantity', 'state'
    )
    list_filter = ('state',)
    list_editable = list_filter
    fieldsets = (
        (None, {'fields': (
            ('from_location', 'to_location'),
            ('from_route_setting', 'to_route_setting'),
            'to_move', 'procurement_detail'
            'quantity', 'state'
        )}),
    )


@admin.register(models.Route)
class RouteAdmin(CommonAdmin):
    list_display = ('name', 'warehouse', 'route_type', 'sequence')
    list_filter = ('warehouse','route_type')
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


@admin.register(models.Procurement)
class ProcurementAdmin(CommonAdmin):
    list_display = ('user', 'state')
    list_filter = ('state',)
    list_editable = ('user',)
    fieldsets = (
        (None, {'fields': ('user', 'state', 'require_procurements')}),
    )


@admin.register(models.ProcurementDetail)
class ProcurementDetailAdmin(CommonAdmin):
    list_display = ('procurement', 'item', 'quantity', 'direct_return', 'route')
    list_filter = ('direct_return',)
    fieldsets = (
        (None, {'fields': ('procurement', 'direct_return', 'route', ('item', 'quantity'))}),
    )
