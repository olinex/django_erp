#!/usr/bin/env python3
#-*- coding:utf-8 -*-

from django.db import models

class ActiveModel(models.Model):
    is_active = models.BooleanField(
        '可用状态',
        blank=False,
        help_text="记录的可用状态,False为不可用,True为可用"
    )

    is_delete = models.BooleanField(
        '删除状态',
        blank=False,
        help_text="记录的删除状态,True删除不可视,False为尚未删除"
    )

    class Meta:
        abstract=True

class LogModel(models.Model):
    create_time = models.DateTimeField(
        '创建时间',
        null=False,
        blank=False,
        auto_now_add=True,
        help_text="记录的创建时间,UTC时间"
    )

    last_modify_time = models.DateTimeField(
        '最后修改时间',
        null=False,
        blank=False,
        auto_now=True,
        help_text="记录的最后修改时间,UTC时间"
    )

    class Meta:
        abstract=True

class CoordinateModel(models.Model):
    lng = models.DecimalField(
        '经度',
        null=True,
        blank=True,
        max_digits=9,
        decimal_places=6,
        default=None,
        help_text='经度,最大为+180.000000,最小为-180.000000')

    lat = models.DecimalField(
        '纬度',
        null=True,
        blank=True,
        max_digits=9,
        decimal_places=6,
        default=None,
        help_text='纬度,最大为+90.000000,最小为-90.000000')

    class Meta:
        abstract = True