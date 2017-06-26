#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from common.state import Statement
from common.fields import (
    ActiveLimitForeignKey,
    ActiveLimitManyToManyField, ActiveLimitOneToOneField,
    SimpleStateCharField
)
from common.abstractModel import BaseModel
from product.utils import QuantityField
from account.utils import PartnerForeignKey
from stock.utils import LocationForeignKey
from djangoperm.db import models
from django.db.models import Q, F, Value, Func
from django.db import transaction



class StockOrder(BaseModel):
    '''单据相关的虚拟类'''

    procurement = ActiveLimitOneToOneField(
        'stock.Procurement',
        null=False,
        blank=False,
        verbose_name='相关需求',
        help_text="订单相关的需求"
    )

    class Meta:
        abstract = True

    @property
    def moves(self):
        return Move.objects.filter(
            procurement_detail_setting__detail__procurement=self.procurement
        )


class StockOrderDetail(BaseModel):
    '''单据相关的明细虚拟类'''
    procurement_detail = ActiveLimitForeignKey(
        'stock.ProcurementDetail',
        null=False,
        blank=False,
        verbose_name='相关需求明细',
        help_text="订单相关的需求明细"
    )

    class Meta:
        abstract = True

    @property
    def moves(self):
        return Move.objects.filter(
            procurement_detail_setting__detail=self.procurement_detail
        )


class Warehouse(BaseModel):
    '''仓库'''
    name = models.CharField(
        '名称',
        null=False,
        blank=False,
        max_length=90,
        help_text="仓库的名称"
    )

    is_inside = models.BooleanField(
        '是否为内部仓库',
        null=False,
        blank=False,
        default=True,
        help_text="是否为内部仓库"
    )

    user = PartnerForeignKey(
        null=False,
        blank=False,
        verbose_name='联系人',
        help_text="仓库的相关合作伙伴或联系人"
    )

    address = ActiveLimitForeignKey(
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

    class States(BaseModel.States):
        inside = Statement(*BaseModel.States.active.query, is_inside=True)
        no_inside = Statement(*BaseModel.States.active.query, is_inside=False)

    def create_zones(self):
        '''
        创建仓库下的各个区域
        :return:dict
        '''
        with transaction.atomic():
            return {
                usage[0]: Zone.objects.get_or_create(
                    warehouse=self,
                    usage=usage[0]
                )
                for usage in Zone.LAYOUT_USAGE
            }


class Zone(BaseModel):
    '''区域'''
    LAYOUT_USAGE = (
        ('stock', '仓库'),
        ('transfer-pick', '分拣流程区域'),
        ('transfer-check', '验货流程区域'),
        ('transfer-pack', '包裹流程区域'),
        ('transfer-stream-wait', '物流等待流程区域'),
        ('transfer-stream-deliver', '物流运输流程区域'),
        ('customer', '顾客区域'),
        ('supplier', '供应商区域'),
        ('produce', '生产区域'),
        ('repair', '返工维修区域'),
        ('scrap', '报废区域'),
        ('close-out', '平仓区域'),
        ('initial', '初始区域')
    )

    self_location = ActiveLimitOneToOneField(
        'stock.Location',
        null=True,
        blank=False,
        verbose_name='库位',
        related_name='self_zone',
        limit_choices_to={
            'is_delete': False,
            'is_active': True,
            'is_virtual': True
        },
        help_text="区域的基本位置"
    )

    warehouse = ActiveLimitForeignKey(
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
        unique_together = (
            ('warehouse', 'usage'),
        )


class Location(BaseModel):
    '''库位'''

    zone = ActiveLimitForeignKey(
        'stock.Zone',
        null=False,
        blank=False,
        verbose_name='区域',
        related_name='locations',
        help_text="库位所属的区域"
    )

    parent_location = ActiveLimitForeignKey(
        'self',
        null=True,
        blank=True,
        verbose_name='上级库位',
        limit_choices_to={'is_delete': False, 'is_active': True, 'is_virtual': True},
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
        unique_together = (
            ('zone', 'x', 'y', 'z'),
        )


class Move(BaseModel):
    '''移动'''

    initial_location = LocationForeignKey(
        null=False,
        blank=False,
        verbose_name='初始库位',
        related_name='spread_moves',
        help_text="移动链的最初的库位"
    )

    end_location = LocationForeignKey(
        null=False,
        blank=False,
        verbose_name='最终库位',
        related_name='converge_moves',
        help_text="移动链的最终的库位"
    )

    from_location = LocationForeignKey(
        null=False,
        blank=False,
        verbose_name='起始库位',
        related_name='out_moves',
        help_text="移动的起始库位"
    )

    to_location = LocationForeignKey(
        null=False,
        blank=False,
        verbose_name='结束库位',
        related_name='in_moves',
        help_text="移动的结束库位"
    )

    to_move = ActiveLimitOneToOneField(
        'self',
        null=True,
        blank=True,
        verbose_name='后续移动',
        related_name='from_move',
        help_text="计划移动链的后续移动"
    )

    procurement_detail_setting = models.ForeignKey(
        'stock.ProcurementFromLocationSettings',
        null=False,
        blank=False,
        verbose_name='需求明细设置',
        help_text="生成该移动的需求明细设置"
    )

    quantity = QuantityField(
        '移动数量',
        null=False,
        blank=False,
        uom='procurement_detail_setting.detail.product.uom',
        help_text="产品的数量"
    )

    state = SimpleStateCharField(
        '状态',
        help_text="移动单的状态"
    )

    def __str__(self):
        return '{} -> {}'.format(
            self.from_location,
            self.to_location
        )

    class Meta:
        verbose_name = '移动'
        verbose_name_plural = '移动'


# class InPickOrder(StockOrder):
#     '''捡入表单'''
#     pass
#
# class OutPickOrder(StockOrder):
#     '''捡出表单'''
#     pass
#
# class CheckOrder(StockOrder):
#     '''验货表单'''
#     pass
#
# class PackOrder(StockOrder):
#     '''打包表单'''
#     pass
#
# class UnPackOrder(StockOrder):
#     '''拆包表单'''
#     pass
#
# class OutOrder(StockOrder):
#     '''出库表单'''
#     pass
#
# class InOrder(StockOrder):
#     '''入库表单'''
#     pass
#
# class StreamOrder(StockOrder):
#     '''物流表单'''
#     pass
#
# class ProduceOrder(StockOrder):
#     '''物料表单'''
#     pass
#
# class RepairOrder(StockOrder):
#     '''维修表单'''
#     pass
#
# class ScrapOrder(BaseModel):
#     '''报废表单'''
#     pass

class Path(BaseModel):
    '''路径'''
    from_location = LocationForeignKey(
        null=False,
        blank=False,
        verbose_name='源库位',
        related_name='out_paths',
        help_text="产品从该库位移出"
    )

    to_location = LocationForeignKey(
        null=False,
        blank=False,
        verbose_name='目标库位',
        related_name='in_paths',
        help_text="产品向该库位移入"
    )

    def __str__(self):
        return '{} -> {}'.format(
            self.from_location,
            self.to_location
        )

    class Meta:
        verbose_name = '路径'
        verbose_name_plural = '路径'
        unique_together = (
            ('from_location', 'to_location')
        )


class Route(BaseModel):
    '''路线'''
    RETURN_METHOD = (
        ('direct', '直接退货'),
        ('fallback', '回滚退货'),
        ('config', '自定义退货')
    )

    name = models.CharField(
        '名称',
        null=False,
        blank=False,
        max_length=190,
        help_text="路线的名称"
    )

    map = models.ShortJSONField(
        null=False,
        blank=False,
        unique=True,
        json_type='list',
        max_length=190,
        help_text="以json格式保存的路径顺序"
    )

    direct_path = ActiveLimitForeignKey(
        'stock.Path',
        null=False,
        blank=False,
        related_name='direct_routes',
        verbose_name="直线路径",
        help_text="表示路线起始库位到最终库位的路径"
    )

    paths = models.ManyToManyField(
        'stock.Path',
        blank=False,
        verbose_name='路径',
        help_text="路线的详细路径"
    )

    return_route = ActiveLimitForeignKey(
        'self',
        null=True,
        blank=True,
        verbose_name='自定义退货路线',
        related_name='origin_routes',
        help_text="路线的自定义退货路线"
    )

    return_method = models.CharField(
        '退货方法',
        null=False,
        blank=False,
        choices=RETURN_METHOD,
        default='direct',
        max_length=10,
        help_text="路线的退货方法"
    )

    sequence = models.PositiveSmallIntegerField(
        '优先级',
        null=False,
        blank=False,
        default=0,
        help_text="在相同起始库位和终点库位的路线的优先级"
    )

    def __str__(self):
        return str(self.direct_path)

    class Meta:
        verbose_name = '路线'
        verbose_name_plural = '路线'


class PackageType(BaseModel):
    '''包裹类型'''
    name = models.CharField(
        '名称',
        null=False,
        blank=False,
        unique=True,
        max_length=90,
        help_text="包裹类型的名称"
    )

    products = models.ManyToManyField(
        'product.Product',
        blank=False,
        through='stock.PackageTypeProductSetting',
        through_fields=('package_type', 'product'),
        verbose_name='产品',
        related_name='package_types',
        help_text="包裹可包装的产品"
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '包裹类型'
        verbose_name_plural = '包裹类型'


class PackageTypeProductSetting(models.Model):
    '''包裹类型产品设置'''
    package_type = ActiveLimitForeignKey(
        'stock.PackageType',
        null=False,
        blank=False,
        verbose_name='包裹类型',
        related_name='package_type_settings',
        help_text="相关的包裹类型"
    )

    product = ActiveLimitForeignKey(
        'product.Product',
        null=False,
        blank=False,
        verbose_name='产品',
        related_name='package_type_settings',
        help_text="相关的产品"
    )

    max_quantity = QuantityField(
        '最大数量',
        null=False,
        blank=False,
        uom='product.uom',
        help_text="包裹类型能够包含该产品的最大数量"
    )

    def __str__(self):
        return '{}-{}({})'.format(
            self.package_type,
            self.product,
            str(self.max_quantity)
        )

    class Meta:
        verbose_name = '包裹类型产品设置'
        verbose_name_plural = '包裹类型产品设置'
        unique_together = (
            ('package_type', 'product'),
        )


class PackageTemplate(BaseModel):
    '''包裹模板'''
    name = models.CharField(
        '名称',
        null=False,
        blank=False,
        unique=True,
        max_length=90,
        help_text="包裹模板的名称"
    )

    package_type = ActiveLimitForeignKey(
        'stock.PackageType',
        null=False,
        blank=False,
        verbose_name='包裹类型',
        help_text="包裹模板的类型"
    )

    products = models.ManyToManyField(
        'product.Product',
        blank=False,
        through='stock.PackageTemplateProductSetting',
        through_fields=('package_template', 'product'),
        verbose_name='产品',
        related_name='package_templates',
        help_text="包裹可包装的产品"
    )

    def __str__(self):
        return str(self.package_type)

    class Meta:
        verbose_name = '包裹模板'
        verbose_name_plural = '包裹模板'


class PackageTemplateProductSetting(models.Model):
    '''包裹模板产品设置'''
    package_template = ActiveLimitForeignKey(
        'stock.PackageTemplate',
        null=False,
        blank=False,
        verbose_name='包裹模板',
        related_name='package_template_settings',
        help_text="相关的包裹模板"
    )

    product = ActiveLimitForeignKey(
        'product.Product',
        null=False,
        blank=False,
        verbose_name='产品',
        related_name='package_template_settings',
        help_text="相关的产品"
    )

    quantity = QuantityField(
        '最大数量',
        null=False,
        blank=False,
        uom='product.uom',
        help_text="包裹模板包含该产品的数量"
    )

    def __str__(self):
        return '{}-{}({})'.format(
            self.package_template,
            self.product,
            str(self.quantity)
        )

    class Meta:
        verbose_name = '包裹模板产品设置'
        verbose_name_plural = '包裹模板产品设置'
        unique_together = (
            ('package_template', 'product'),
        )


class PackageNode(models.Model):
    '''包裹节点'''
    name = models.CharField(
        '名称',
        null=False,
        blank=False,
        unique=True,
        max_length=90,
        help_text="打包方法的名称"
    )

    parent_node = models.ForeignKey(
        'self',
        null=True,
        default=None,
        verbose_name='父节点',
        related_name='child_nodes',
        help_text="包裹该节点的节点"
    )

    template = ActiveLimitForeignKey(
        'stock.PackageTemplate',
        null=False,
        blank=False,
        verbose_name='包裹类型',
        help_text="打包方法相关的包裹类型"
    )

    quantity = models.PositiveSmallIntegerField(
        '数量',
        null=False,
        blank=False,
        default=1,
        help_text="包裹的数量"
    )

    index = models.CharField(
        '索引',
        null=False,
        blank=True,
        default='',
        max_length=190,
        help_text="该包裹所在包裹树的索引"
    )

    level = models.PositiveSmallIntegerField(
        '树层',
        null=False,
        blank=False,
        default=0,
        help_text="该包裹所距离所在包裹树的根的距离"
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '包裹节点'
        verbose_name_plural = '包裹节点'
        unique_together = (
            ('parent_node', 'template'),
        )

    @property
    def root_node(self):
        '''
        获取当前节点的根节点
        :return: PackageNode Instance
        '''
        if self.index:
            return self.__class__.objects.filter(
                id=int(self.index.split('-')[0]),
                level=0
            )
        return self

    @property
    def all_child_nodes(self):
        '''
        获取当前节点下所有的子孙节点
        :return: PackageNode Queryset
        '''
        return self.__class__.objects.filter(
            index__startswith='{}-{}-'.format(self.index, self.id)
        )

    @property
    def all_parent_nodes(self):
        '''
        获取当前节点的所有父节点
        :return: PackageNode Queryset
        '''
        return self.__class__.objects.filter(
            id__in=[int(node_id) for node_id in self.index.split('-')[:-1]]
        )

    @property
    def sibling_nodes(self):
        '''
        获取当前节点下排除自己的的所有兄弟节点,并排除自身,若为根节点,则返回除了自己之外的所有根节点
        :return: PackageNode Queryset
        '''
        return self.__class__.objects.filter(
            index=self.index,
            level=self.level
        ).exclude(id=self.id)

    @property
    @classmethod
    def root_nodes(cls):
        '''
        获取所有根节点
        :return: PackageNode Queryset
        '''
        return cls.objects.filter(
            parent_node=None,
            index='',
            level=0
        )

    def change_parent_node(self, node):
        '''
        修改父节点时,同步更新该节点下的所有子节点key和level
        :node:PackageNode Instance
        :return:True
        '''
        with transaction.atomic():
            new_index = '{}-{}-'.format(node.index, str(node.id))
            old_index = self.index
            self.all_child_nodes.update(
                index=Func(F('index'), Value(new_index), Value(old_index), function='replace'),
                level=F('level') + Value(node.level - self.level)
            )
            self.index = new_index
            self.parent_node = node
            self.save()


class Procurement(BaseModel):
    '''需求'''
    to_location = LocationForeignKey(
        null=False,
        blank=False,
        verbose_name='库位',
        help_text="需求产生的库位"
    )

    user = PartnerForeignKey(
        null=False,
        blank=False,
        verbose_name='合作伙伴',
        help_text="提出需求的相关合作伙伴"
    )

    state = SimpleStateCharField(
        '状态',
        help_text="需求单的状态"
    )

    def __str__(self):
        return '{}-{}'.format(str(self.user), str(self.to_location))

    class Meta:
        verbose_name = '需求'
        verbose_name_plural = '需求'

class ProcurementDetail(BaseModel):
    '''需求明细'''
    from_locations = models.ManyToManyField(
        'stock.Location',
        blank=False,
        through='stock.ProcurementFromLocationSettings',
        through_fields=('detail', 'location'),
        verbose_name='来源位置',
        related_name='procurement_details',
        help_text="需求产品的来源位置"
    )

    product = ActiveLimitForeignKey(
        'product.Product',
        null=False,
        blank=False,
        verbose_name='产品',
        help_text="明细相关的产品"
    )

    lot = ActiveLimitForeignKey(
        'product.Lot',
        null=True,
        blank=True,
        default=None,
        verbose_name="批次",
        help_text="产品所属的批次"
    )

    procurement = ActiveLimitForeignKey(
        'stock.Procurement',
        null=False,
        blank=False,
        verbose_name='需求',
        related_name='procurement_details',
        help_text="需求明细所属的需求"
    )

    def __str__(self):
        return '{}/{}'.format(str(self.procurement), str(self.product))

    class Meta:
        verbose_name = "需求明细"
        verbose_name_plural = "需求明细"
        unique_together = ('procurement', 'product')

    @property
    def quantity(self):
        return sum(
            ProcurementFromLocationSettings.objects.filter(
                detail=self).values_list('quantity', flat=True)
        )


class ProcurementFromLocationSettings(models.Model):
    '''需求产品指定的来源位置'''
    detail = ActiveLimitForeignKey(
        'stock.ProcurementDetail',
        null=False,
        blank=False,
        verbose_name='需求明细',
        related_name='procurement_from_location_settings',
        help_text="相关的需求"
    )

    location = LocationForeignKey(
        null=False,
        blank=False,
        verbose_name='来源位置',
        related_name='procurement_from_location_settings',
        help_text="相关的位置"
    )

    quantity = QuantityField(
        '移动数量',
        null=False,
        blank=False,
        uom='product.uom',
        help_text="产品的数量"
    )

    route = ActiveLimitForeignKey(
        'stock.Route',
        null=False,
        blank=False,
        verbose_name='路线',
        help_text="与需求相关的路线"
    )

    def __str__(self):
        return '{}/{}'.format(str(self.detail), str(self.location))

    class Meta:
        verbose_name = '需求产品来源设置'
        verbose_name_plural = '需求产品来源设置'
        unique_together = (
            ('detail', 'location'),
        )