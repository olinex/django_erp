#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# from . import models
# from django.contrib import admin
# from django_erp.common.admins import CommonTabInLine


# class CityInline(admin.TabularInline):
#     model = models.City
#     fieldsets = (
#         (None, {'fields': ('name', 'sequence')}),
#     )
#
#
# class RegionInline(admin.TabularInline):
#     model = models.Region
#     fieldsets = (
#         (None, {'fields': ('name', 'sequence')}),
#     )
#
#
# class AddressInline(CommonTabInLine):
#     model = models.Address
#     fieldsets = (
#         (None, {'fields': ('name',)}),
#     )
#
#
# @admin.register(models.Province)
# class ProvinceAdmin(admin.ModelAdmin):
#     list_display = ('id', 'country', 'name')
#     list_display_links = ('name',)
#     search_fields = ('name',)
#     list_editable = ('country',)
#     fieldsets = (
#         (None, {'fields': ('country', 'name')}),
#     )
#     inlines = [
#         CityInline
#     ]
#
#
# @admin.register(models.City)
# class CityAdmin(admin.ModelAdmin):
#     list_display = ('id', 'province', 'name')
#     list_display_links = ('name',)
#     search_fields = ('name',)
#     list_editable = ('province',)
#     fieldsets = (
#         (None, {'fields': ('province', 'name')}),
#     )
#     inlines = (
#         RegionInline,
#     )
#
#
# @admin.register(models.Region)
# class RegionAdmin(admin.ModelAdmin):
#     list_display = ('id', 'city', 'name')
#     list_display_links = ('name',)
#     search_fields = ('name',)
#     list_editable = ('city',)
#     fieldsets = (
#         (None, {'fields': ('city', 'name')}),
#     )
#     inlines = (
#         AddressInline,
#     )
#
#
# @admin.register(models.Partner)
# class PartnerAdmin(admin.ModelAdmin):
#     list_display = ('id', 'name', 'phone', 'address', 'is_company', 'sale_able', 'purchase_able')
#     list_display_links = ('name',)
#     list_filter = ('is_company', 'sale_able', 'purchase_able')
#     search_fields = ('name', 'phone', 'address__name')
#     list_editable = ('phone', 'is_company', 'sale_able', 'purchase_able')
#     fieldsets = (
#         (None, {'fields': (
#             'name', 'phone', 'address',
#             'default_send_address',
#             'usual_send_addresses',
#             'is_active', 'managers',
#             ('is_company', 'sale_able', 'purchase_able')
#         )}),
#     )
#
#
# @admin.register(models.Profile)
# class ProfileAdmin(admin.ModelAdmin):
#     list_display = (
#         'user', 'sex', 'phone', 'online_notice', 'mail_notice', 'language', 'address'
#     )
#     list_display_links = ('user',)
#     list_filter = (
#         'sex', 'online_notice', 'mail_notice'
#     )
#     search_fields = ('phone', 'user__username')
#     list_editable = (
#         'phone', 'sex', 'online_notice', 'mail_notice', 'language'
#     )
#     fieldsets = (
#         (None, {'fields': (
#             'user', 'sex', 'phone', 'language', ('online_notice', 'mail_notice'), 'address'
#         )}),
#     )
