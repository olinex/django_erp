#!/usr/bin/env python3
#-*- coding:utf-8 -*-

from django.conf import settings

from apps.django_perm import models
from common.abstractModel import BaseModel
from common.fields import ActiveLimitForeignKey


class File(BaseModel):
    '''文件虚拟类'''
    md5 = models.CharField(
        '文件md5值',
        primary_key=True,
        max_length=40,
        help_text="文件的md5主键值"
    )

    size = models.PositiveIntegerField(
        '文件大小',
        null=False,
        default=0,
        help_text="保存的文件的大小,单位为KB"
    )

    name = models.CharField(
        '文件名称',
        null=False,
        blank=False,
        max_length=60,
        help_text="文件的名称"
    )

    uploader = ActiveLimitForeignKey(
        settings.AUTH_USER_MODEL,
        null=False,
        blank=False,
        verbose_name='创建者',
        help_text="文件的上传者"
    )

    class Meta:
        abstract = True