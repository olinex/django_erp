#!/usr/bin/env python3
#-*- coding:utf-8 -*-

from . import models
from django.contrib import admin
from common.admin import  CommonAdmin,CommonTabInLine

class AttributeInline(CommonTabInLine):
    model=models.Attribute
    fieldsets = (
        (None,{'fields':('name','value')}),
    )

@admin.register(models.ProductCategory)
class ProductCategoryAdmin(CommonAdmin):
    list_display = ('name','sequence')
    search_fields = ('name',)
    list_editable = ('name','sequence')
    fieldsets = (
        (None,{'fields':('name','sequence')}),
    )

@admin.register(models.Attribute)
class AttributeAdmin(CommonAdmin):
    list_display = ('id','name','value')
    search_fields = ('name',)
    list_editable = ('name',)
    fieldsets = (
        (None,{'fields':('name','value')}),
    )

@admin.register(models.UOM)
class UOMAdmin(CommonAdmin):
    list_display = (
        'name','symbol','decimal_places',
        'round_method','ratio_type','ratio',
        'category'
    )
    list_filter = ('round_method','ratio_type','category')
    list_display_links = ('name',)
    search_fields = ('name','symbol')
    list_editable = (
        'decimal_places','round_method',
        'ratio_type','ratio','category'
    )
    fieldsets = (
        (None,{'fields':(
            'name','symbol',
            ('decimal_places','ratio'),
            'round_method','ratio_type','category'
        )}),
    )

@admin.register(models.ProductTemplate)
class ProductTemplateAdmin(CommonAdmin):
    list_display = (
        'id','name','uom','sequence',
        'category',
    )
    list_filter = ('category',)
    search_fields = ('name','uom')
    list_editable = ('name','sequence','category')
    fieldsets = (
        (None,{'fields':(
            'name','attributes','uom',
            'sequence','detail','in_description',
            'out_description'
        )}),
    )

@admin.register(models.Product)
class ProductAdmin(CommonAdmin):
    list_display = (
        'id','template','in_code',
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
            'template','attributes',
            ('in_code','out_code'),
            ('weight','volume'),
            ('salable','purchasable','rentable')
        )}),
    )

