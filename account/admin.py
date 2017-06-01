#!/usr/bin/env python3
#-*- coding:utf-8 -*-

from . import models
from django.contrib import admin
from common.admin import CommonAdmin,CommonTabInLine

class CityInline(CommonTabInLine):
    model=models.City
    fieldsets = (
        (None,{'fields':('name','is_active','is_delete')}),
    )

class RegionInline(CommonTabInLine):
    model=models.Region
    fieldsets = (
        (None,{'fields':('name','is_active','is_delete')}),
    )

class AddressInline(CommonTabInLine):
    model=models.Address
    fieldsets = (
        (None,{'fields':('name','is_active','is_delete')})
    )

class PartnerInline(CommonTabInLine):
    model=models.Partner
    fieldsets = (
        (None,{'fields':('name','can_sale','can_purchase','is_active','is_delete')})
    )

@admin.register(models.Province)
class ProvinceAdmin(CommonAdmin):
    list_display = ('id','country','name')
    search_fields = ('name',)
    list_editable = ('name',)
    fieldsets = (
        (None,{'fields':('country','name','is_active')}),
    )
    inlines = [
        CityInline
    ]

@admin.register(models.City)
class CityAdmin(CommonAdmin):
    list_display = ('id','province','name')
    search_fields = ('name',)
    list_editable = ('name',)
    fieldsets = (
        (None,{'fields':('province','name','is_active')}),
    )
    inlines = (
        RegionInline,
    )

@admin.register(models.Region)
class RegionAdmin(CommonAdmin):
    list_display = ('id','city','name')
    search_fields = ('name',)
    list_editable = ('name',)
    fieldsets = (
        (None,{'fields':('city','name','is_active')}),
    )

@admin.register(models.Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'sex', 'phone','online_notice','mail_notice','language')
    list_filter = ('sex','online_notice','mail_notice')
    search_fields = ('phone', 'user__username')
    list_per_page = 20
    list_editable = ('phone', 'sex','online_notice','mail_notice','language')
    fieldsets = (
        (None,{'fields':(
            'user','sex','phone','language',('online_notice','mail_notice'))}),
    )

@admin.register(models.Partner)
class PartnerAdmin(CommonAdmin):
    list_display = ('id','name','tel','address','can_sale','can_purchase')
    list_filter = ('can_sale','can_purchase')
    search_fields = ('name','tel','address__name')
    list_editable = ('name','tel','can_sale','can_purchase')
    fieldsets = (
        (None,{'fields':(
            'name','tel','address',
            'default_send_address',
            'usual_send_addresses',
            'is_active',
            ('can_sale','can_purchase')
        )}),
    )

@admin.register(models.Company)
class CompanyAdmin(CommonAdmin):
    list_display = ('id','name','tel','address','can_sale','can_purchase')
    list_display_links = ('id',)
    list_filter = ('can_sale','can_purchase')
    search_fields = ('name','tel','address__name')
    list_editable = ('name','tel','can_sale','can_purchase')
    fieldsets = (
        (None,{'fields':(
            'name','tel','address',
            'default_send_address',
            'usual_send_addresses',
            'is_active',
            'belong_customers',
            ('can_sale','can_purchase'),
        )}),
    )






