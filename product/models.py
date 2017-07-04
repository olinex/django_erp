#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from decimal import Decimal as D
from django.db import transaction
from common import state
from common.abstractModel import BaseModel
from common.fields import (
    ActiveLimitForeignKey, ActiveLimitManyToManyField, MD5CharField,
    ActiveLimitOneToOneField
)
from djangoperm.db import models


class ProductCategory(BaseModel, state.StateMachine):
    '''产品分类'''
    name = models.CharField(
        '种类名称',
        unique=True,
        max_length=90,
        help_text="产品的种类"
    )

    sequence = models.PositiveIntegerField(
        '排序',
        null=False,
        blank=True,
        default=0,
        help_text="产品种类的排序"
    )

    class Meta:
        verbose_name = '产品分类'
        verbose_name_plural = '产品分类'

    def __str__(self):
        return self.name


class Product(BaseModel):
    '''产品'''
    template = ActiveLimitForeignKey(
        'product.ProductTemplate',
        null=False,
        blank=False,
        on_delete=models.PROTECT,
        verbose_name='模板',
        help_text="产品的模板"
    )

    attributes = models.JSONField(
        '产品属性字典',
        null=False,
        blank=True,
        default={},
        json_type='dict',
        help_text="根据产品模板的属性列表设置的产品属性值字典"
    )

    attributes_md5 = models.CharField(
        '产品属性字典的md5值',
        null=False,
        blank=False,
        max_length=40,
        help_text='产品属性字典json值的md5值'
    )

    in_code = models.CharField(
        '内部编码',
        null=False,
        blank=True,
        default='',
        max_length=190,
        help_text="产品模板的内部编码"
    )

    out_code = models.CharField(
        '外部编码',
        null=False,
        blank=True,
        default='',
        max_length=190,
        help_text="产品模板的外部编码"
    )

    weight = models.DecimalField(
        '重量',
        null=False,
        blank=True,
        max_digits=24,
        decimal_places=12,
        default=D('0.0'),
        help_text="产品的重量,单位为kg"
    )

    volume = models.DecimalField(
        '体积',
        null=False,
        blank=True,
        max_digits=24,
        decimal_places=12,
        default=D('0.0'),
        help_text="产品的体积,单位为m³"
    )

    salable = models.BooleanField(
        '销售状态',
        null=False,
        blank=True,
        default=False,
        help_text="商品的销售状态,如果为False则不能被销售"
    )

    purchasable = models.BooleanField(
        '采购状态',
        null=False,
        blank=True,
        default=False,
        help_text="商品的采购状态,如果为False则不能被采购"
    )

    rentable = models.BooleanField(
        '租借状态',
        null=False,
        blank=True,
        default=False,
        help_text="商品的租借状态,如果为False则不能通过被租借"
    )

    def __str__(self):
        return (
            self.template.name +
            '(' + self.attributes_str + ')'
        )

    class Meta:
        verbose_name = '产品'
        verbose_name_plural = '产品'
        unique_together = ('template', 'attributes_md5')

    @property
    def attributes_str(self):
        return '/'.join(
            [
                '{}:{}'.format(key, value)
                for key, value in self.attributes.items()
            ]
        )


class ProductTemplate(BaseModel):
    '''产品模版'''
    name = models.CharField(
        '名称',
        unique=True,
        null=False,
        blank=False,
        max_length=190,
        help_text="产品模板的名称"
    )

    attributes = ActiveLimitManyToManyField(
        'product.Attribute',
        verbose_name='默认属性',
        help_text="产品模板的默认属性"
    )

    uom = ActiveLimitForeignKey(
        'product.UOM',
        null=False,
        blank=False,
        verbose_name='单位',
        on_delete=models.PROTECT,
        help_text='产品的默认计量单位'
    )

    sequence = models.PositiveIntegerField(
        '排序',
        null=False,
        blank=True,
        default=0,
        help_text="产品显示的排序"
    )

    detail = models.CharField(
        '提示',
        null=False,
        blank=True,
        default='',
        max_length=190,
        help_text="产品的提示"
    )

    in_description = models.TextField(
        '内部说明',
        null=False,
        blank=True,
        default='',
        help_text="产品内部的说明"
    )

    out_description = models.TextField(
        '外部说明',
        null=False,
        blank=True,
        default='',
        help_text="产品的外部说明"
    )

    category = models.ForeignKey(
        'product.ProductCategory',
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        verbose_name='产品种类',
        help_text="产品的分类"
    )

    class Meta:
        verbose_name = '产品模板'
        verbose_name_plural = '产品模板'

    def __str__(self):
        self.name

    @property
    def attribute_combination(self):
        from itertools import product
        attributes = self.attributes.value_lists('name', 'value')
        key_list = [attr[0] for attr in attributes]
        for value_tuple in product(attr[1] for attr in attributes):
            yield dict(zip(key_list,value_tuple))

    def sync_create_products(self):
        import json
        from hashlib import md5
        from django.core.serializers.json import DjangoJSONEncoder
        with transaction.atomic():
            for attributes in self.attribute_combination:
                m = md5()
                m.update(json.dumps(attributes, cls=DjangoJSONEncoder).encode('utf8'))
                self.attributes.through.objects.get_or_create(
                    template=self,
                    attributes_md5=m.hexdigest(),
                    defaults={
                        'attributes': attributes,
                        'is_active': False
                    }
                )

class Attribute(BaseModel):
    '''属性'''
    name = models.CharField(
        '名称',
        null=False,
        blank=False,
        unique=True,
        max_length=190,
        help_text="产品属性的名称"
    )

    value = models.JSONField(
        '值',
        null=False,
        blank=False,
        json_type='list',
        help_text="JSON格式保存的属性可选值"
    )

    class Meta:
        verbose_name = '属性'
        verbose_name_plural = '属性'

    def __str__(self):
        return self.name


class UOM(BaseModel):
    '''计量单位'''
    UOM_CATEGORY = (
        ('m', '米'),
        ('kg', '千克'),
        ('s', '秒'),
        ('A', '安培'),
        ('K', '开尔文'),
        ('J', '焦耳'),
        ('m²', '平方米'),
        ('m³', '立方米'),
        ('unit', '个'),
        ('yuan', '元')
    )

    ROUND_METHOD = (
        ('ROUND_CEILING', '趋向无穷大取整'),
        ('ROUND_DOWN', '趋向零取整'),
        ('ROUND_FLOOR', '趋向负无穷大取整'),
        ('ROUND_HALF_DOWN', '末位大于五反向零取整,否则趋向零取整'),
        ('ROUND_HALF_EVEN', '末位大于五反向零取整,小于五趋向零取整,遇五前位为奇数反向零取整'),
        ('ROUND_HALF_UP', '末位大于等于五反向零取整,否则趋向零取整'),
        ('ROUND_UP', '反向零取整'),
        ('ROUND_05UP', '取整位数为零或五时反向零取整,否则趋向零取整')
    )

    name = models.CharField(
        '名称',
        null=False,
        blank=False,
        max_length=20,
        unique=True,
        help_text='单位名称'
    )

    symbol = models.CharField(
        '符号',
        null=False,
        blank=False,
        unique=True,
        max_length=10,
        help_text="单位符号"
    )

    decimal_places = models.PositiveSmallIntegerField(
        '小数精度',
        null=False,
        blank=False,
        default=3,
        help_text="数量转为浮点数显示时,数量的小数个数"
    )

    round_method = models.CharField(
        '舍入方法',
        null=False,
        blank=False,
        max_length=10,
        choices=ROUND_METHOD,
        default='ROUND_CEILING',
        help_text='根据单位做精度转换时单位的默认舍入方法'
    )

    ratio_type = models.CharField(
        '比率类型',
        null=False,
        blank=False,
        default='greater',
        choices=[
            ('greater', '大于'),
            ('smaller', '小于'),
            ('equal', '等于')
        ],
        max_length=10,
        help_text="单位与主单位的比较方式"
    )

    ratio = models.DecimalField(
        '比率',
        max_digits=24,
        decimal_places=12,
        null=False,
        blank=False,
        help_text="与对应单位类型的标准单位的比值"
    )

    category = models.CharField(
        '单位类型',
        null=False,
        blank=False,
        max_length=5,
        choices=UOM_CATEGORY,
        help_text="单位所属的单位类型,仅当单位属于同一类型时,方可互相转换"
    )

    class Meta:
        verbose_name = '单位'
        verbose_name_plural = '单位'

    def __str__(self):
        return self.name + '(' + self.symbol + ')'

    def floor_value(self, value):
        '''
        将value转换为单位的精度
        :param value: decimal
        :return: decimal
        '''
        import decimal
        with decimal.localcontext() as ctx:
            ctx.prec = 24
            return value.quantize(
                decimal.Decimal('0.' + ('0' * self.decimal_places)),
                rounding=getattr(decimal, self.round_method),
            )


class Lot(BaseModel):
    '''批次'''
    name = models.CharField(
        '名称',
        null=False,
        blank=False,
        unique=True,
        max_length=90,
        help_text="批次的名称"
    )

    product = ActiveLimitForeignKey(
        'product.Product',
        null=False,
        blank=False,
        verbose_name='产品',
        help_text="批次相关的产品"
    )

    class Meta:
        verbose_name = '批次'
        verbose_name_plural = '批次'

    def __str__(self):
        return self.name


class Barcode(BaseModel):
    '''条形码类'''
    BARCODE_MODE = (
        ('Standard39', '标准39'),
    )

    product = ActiveLimitOneToOneField(
        'product.Product',
        null=False,
        blank=False,
        verbose_name='产品',
        help_text="条形码对应的产品"
    )

    mode = models.CharField(
        '条形码模式',
        null=False,
        blank=False,
        max_length=20,
        choices=BARCODE_MODE,
        help_text="条形码模式"
    )

    code = models.JSONField(
        '条形码编码值',
        null=False,
        blank=False,
        json_type='dict',
        help_text="条形码的编码值字典"
    )

    have_quiet = models.BooleanField(
        '是否含有静区',
        default=False,
        help_text="条形码是否还有空白区"
    )

    is_iso_scale = models.BooleanField(
        '是否被iso收录',
        default=False,
        help_text="条形码是否已被iso标准收录"
    )

    check_sum = models.BooleanField(
        '是否检查合计',
        default=False,
        help_text="条形码是否检查合计"
    )
