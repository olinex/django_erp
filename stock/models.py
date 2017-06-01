#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from djangoperm.db import models
from common.abstractModel import BaseModel
from common.statemachine import state

class Warehouse(BaseModel,state.StateMachine):
    '''仓库'''
    name = models.CharField(
        '名称',
        null=False,
        blank=False,
        max_length=90,
        help_text="仓库的名称"
    )

    is_inside = models.BinaryField(
        '是否为内部仓库',
        null=False,
        blank=False,
        default=True,
        help_text="是否为内部仓库"
    )

    partner = models.ForeignKey(
        'account.Partner',
        null=False,
        blank=False,
        verbose_name='联系人',
        help_text="仓库的相关合作伙伴或联系人"
    )

    address = models.ForeignKey(
        'account.Address',
        null=False,
        blank=False,
        verbose_name='地址',
        help_text="仓库的地理位置"
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '仓库'
        verbose_name_plural = '仓库'

    class States:
        delete = state.Statement(delete=True)
        undelete = state.Statement(delete=False)
        active = state.Statement(inherits=undelete,active=True)
        deactive = state.Statement(inherits=undelete,active=False)

class Zone(BaseModel):
    '''区域'''
    LAYOUT_USAGE = (
        ('warehouse', '仓库'),
        ('transfer-pick', '分拣流程区域'),
        ('transfer-pack', '打包流程区域'),
        ('transfer-check', '验货流程区域'),
        ('transfer-out', '出库流程区域'),
        ('transfer-in', '入库流程区域'),
        ('scrap', '报废区域'),
        ('close-out', '平仓区域'),
        ('init', '初始区域')
    )

    self_location = models.OneToOneField(
        'stock.Location',
        null=False,
        blank=False,
        verbose_name='库位',
        related_name='self_zone',
        help_text="区域的基本位置"
    )

    warehouse = models.ForeignKey(
        'stock.Warehouse',
        null=False,
        blank=False,
        verbose_name='仓库',
        help_text="区域所属的仓库"
    )

    usage = models.CharField(
        '用途',
        null=False,
        blank=False,
        choices=LAYOUT_USAGE,
        max_length=20,
        default='container',
        help_text="区域的用途"
    )

    def __str__(self):
        str(self.warehouse) + '/' + self.usage

    class Meta:
        verbose_name = '区域'
        verbose_name_plural = '区域'

class Location(BaseModel):

    warehouse = models.ForeignKey(
        'stock.Warehouse',
        null=False,
        blank=False,
        verbose_name='仓库',
        help_text="库位所属的仓库"
    )

    zone = models.ForeignKey(
        'stock.Zone',
        null=False,
        blank=False,
        verbose_name='区域',
        related_name='locations',
        help_text="库位所属的区域"
    )

    parent_location = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        verbose_name='上级库位',
        help_text="库位所属的上级库位,若库位为区域的基本库位,则必须为虚拟库位"
    )

    is_virtual = models.BooleanField(
        '虚拟库位',
        blank=True,
        default=False,
        help_text="库位的虚拟状态"
    )

    x = models.CharField(
        'X',
        null=False,
        blank=True,
        max_length=90,
        help_text="库位的X轴坐标"
    )

    y = models.CharField(
        'Y',
        null=False,
        blank=True,
        max_length=90,
        help_text="库位的Y轴坐标"
    )

    z = models.CharField(
        'Z',
        null=False,
        blank=True,
        max_length=90,
        help_text="库位的Z轴坐标"
    )

    def __str__(self):
        return str(self.zone) + '(X:{},Y:{},Z:{})'.format(
            self.x,
            self.y,
            self.z
        )

    class Meta:
        verbose_name = "库位"
        verbose_name_plural = "库位"
