#!/usr/bin/env python3
#-*- coding:utf-8 -*-

from . import models
from django.contrib import admin
from common.admin import CommonAdmin

@admin.register(models.Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'sex', 'phone','online_notice','mail_notice','language')
    list_filter = ('sex','online_notice','mail_notice')
    search_fields = ('phone', 'user__username')
    list_per_page = 20
    list_editable = ('phone', 'sex','online_notice','mail_notice','language')


