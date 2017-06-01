#!/usr/bin/env python3
#-*- coding:utf-8 -*-

from djangoperm.db import models

class BaseModel(models.Model):
    is_active = models.BooleanField(
        '可用状态',
        blank=False,
        default=True,
        help_text="记录的可用状态,False为不可用,True为可用"
    )

    is_delete = models.BooleanField(
        '删除状态',
        blank=False,
        default=False,
        help_text="记录的删除状态,True删除不可视,False为尚未删除"
    )

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

    statements = {}

    def get_states(self):
        '''获得所有的状态'''
        self.statements.update({
            'usable':{
                'is_delete':False,
            },
            'deleted':{
                'is_delete':True,
            },
            'active':{
                'is_delete':False,
                'is_active':True,
            },
            'deactive':{
                'is_delete':False,
                'is_active':False,
            },
        })
        return self.statements

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