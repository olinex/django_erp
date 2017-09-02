#!/usr/bin/env python3
#-*- coding:utf-8 -*-

from django.contrib import admin

from common.admin import CommonAdmin, CommonTabInLine
from . import models


class AttributeInline(CommonTabInLine):
    model= models.Attribute
    fieldsets = (
        (None,{'fields':('name','value','extra_price')}),
    )

class LotInline(CommonTabInLine):
    model= models.Lot
    fieldsets = (
        (None,{'fields':('name',)}),
    )

class ValidateActionInline(CommonTabInLine):
    model= models.ValidateAction
    fieldsets = (
        (None,{'fields':('symbol','name','uom','explain')}),
    )

@admin.register(models.ProductCategory)
class ProductCategoryAdmin(CommonAdmin):
    list_display = ('name','sequence')
    list_display_links = ('name',)
    search_fields = ('name',)
    list_editable = ('sequence',)
    fieldsets = (
        (None,{'fields':('name','sequence')}),
    )

@admin.register(models.Attribute)
class AttributeAdmin(CommonAdmin):
    list_display = ('name','value','extra_price',)
    search_fields = ('name',)
    list_editable = ('name',)
    fieldsets = (
        (None,{'fields':('name','value','extra_price')}),
    )

@admin.register(models.UOM)
class UOMAdmin(CommonAdmin):
    list_display = (
        'name','symbol','decimal_places',
        'round_method','ratio','category'
    )
    list_filter = ('round_method','category')
    list_display_links = ('name',)
    search_fields = ('name','symbol')
    list_editable = (
        'decimal_places','round_method','ratio','category'
    )
    fieldsets = (
        (None,{'fields':(
            'name','symbol',
            ('decimal_places','ratio'),
            'round_method','category'
        )}),
    )

@admin.register(models.ProductTemplate)
class ProductTemplateAdmin(CommonAdmin):
    list_display = (
        'name','uom','sequence',
        'category','detail'
    )
    list_filter = ('category',)
    search_fields = ('name','uom')
    list_editable = ('name','sequence','category')
    fieldsets = (
        (None,{'fields':(
            'name','attributes','detail',
            ('uom','stock_type'),
            ('in_description','out_description'),
            ('category','sequence'),
        )}),
    )


@admin.register(models.Product)
class ProductAdmin(CommonAdmin):
    list_display = (
        'id','template','attributes','prices','in_code',
        'out_code','weight','volume',
        'salable','purchasable','rentable'
    )
    list_filter = ('salable','purchasable','rentable')
    search_fields = ('in_code','out_code','detail')
    list_editable = (
        'in_code','out_code','weight','volume',
        'salable','purchasable','rentable'
    )
    fieldsets = (
        (None,{'fields':(
            'template','attributes','prices',
            ('in_code','out_code'),
            ('weight','volume'),
            ('salable','purchasable','rentable')
        )}),
    )
    inlines = (
        LotInline,
    )

@admin.register(models.Validation)
class ValidationAdmin(CommonAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    list_display_links = ('name',)
    fieldsets = (
        (None,{'fields':(
            'name','actions'
        )}),
    )
    inlines = (
        ValidateActionInline,
    )

