#!/usr/bin/env python3
#-*- coding:utf-8 -*-

from . import models
from django.contrib import admin


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'sex', 'phone','online_notice')
    list_filter = ('sex','online_notice')
    search_fields = ('phone', 'user')
    list_per_page = 50
    list_editable = ('phone', 'sex','online_notice')

admin.site.register(models.Profile, ProfileAdmin)
