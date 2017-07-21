#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from decimal import Decimal as D
from common import Redis
from common.state import Statement,StateMachine
from common.fields import (
    ActiveLimitForeignKey,
    ActiveLimitManyToManyField, ActiveLimitOneToOneField,
    SimpleStateCharField
)
from common.abstractModel import BaseModel, TreeModel
from product.utils import QuantityField
from account.utils import PartnerForeignKey
from stock.utils import LocationForeignKey
from djangoperm.db import models
from django.db import transaction
from django.db.models import Q,F


class CacheLocation(object):
    '''库位的缓存类'''

    def __init__(self, location):
        self.location = location

    @property
    def cache_name(self):
        return 'warehouse_{}_zone_{}_location_{}'.format(
            self.location.zone.warehouse.pk,
            self.location.zone.pk,
            self.location.pk
        )

    def refresh(self, product, quantity, pipe=None):
        redis = pipe or Redis()
        redis.zincrby(self.cache_name, 'product_{}'.format(product.pk), quantity)

    def lock(self,product,quantity,pipe=None):
        redis = pipe or Redis()
        redis.zincrby(self.cache_name, 'product_lock_{}'.format(product.pk), -quantity)

    def free_all(self,product,pipe=None):
        redis = pipe or Redis()
        redis.zrem(self.cache_name,'product_lock_{}'.format(product.pk))

    def sync(self):
        '''同步库存的产品数量'''
        if self.location.check_states('no_virtual'):
            from product.models import Product
            redis = Redis()
            pipe = redis.pipeline()
            pipe.delete(self.cache_name)
            product_set = set(
                move.procurement_detail_setting.detail.product
                for move in Move.get_state_queryset('done')
            )
            for product in product_set:
                self.refresh(
                    product,
                    self.location.in_sum(product) - self.location.out_sum(product),
                    pipe=pipe
                )
            pipe.execute()
            return True
        return False


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

    def create_zones(self):
        '''
        创建仓库下的各个区域
        :return:dict
        '''
        with transaction.atomic():
            for usage in Zone.LAYOUT_USAGE:
                zone = Zone.objects.create(
                    warehouse=self,
                    usage=usage[0]
                )
                location = Location.objects.create(
                    zone=zone,
                    parent_node=None,
                    is_virtual=True,
                    x='', y='', z=''
                )
                zone.root_location = location
                zone.save()

    @property
    def leaf_child_locations(self):
        '''获得仓库下所有的叶节点库位'''
        return Location.get_state_queryset('no_virtual').filter(zone__warehouse=self)

    @property
    @classmethod
    def leaf_child_locations_cache_name(cls):
        from functools import reduce
        return reduce(
            lambda a, b: a + b,
            [
                [node.cache.cache_name for node in warehouse.leaf_child_locations]
                for warehouse in cls.get_state_queryset('active')
            ]
        )

    def get_product_quantity(self, product, usage='all'):
        if usage in Zone.States.USAGE_STATES.keys():
            zone = Zone.get_state_queryset(usage, self.zones.all())[0]
            return zone.get_product_quantity(product)
        elif usage == 'all':
            redis = Redis()
            return D(redis.zinterstore(
                dest=('product_{}'.format(product.pk),),
                keys=[location.cache.cache_name for location in self.leaf_child_locations]
            )
            )
        else:
            return D('0')


class Zone(BaseModel):
    '''区域'''
    LAYOUT_USAGE = (
        ('stock', '仓库'),
        ('pick', '分拣流程区域'),
        ('check', '验货流程区域'),
        ('pack', '包裹流程区域'),
        ('wait', '物流等待流程区域'),
        ('deliver', '物流运输流程区域'),
        ('customer', '顾客区域'),
        ('supplier', '供应商区域'),
        ('produce', '生产区域'),
        ('repair', '返工维修区域'),
        ('scrap', '报废区域'),
        ('closeout', '平仓区域'),
        ('initial', '初始区域'),
        ('midway', '中途岛区域')
    )

    warehouse = ActiveLimitForeignKey(
        'stock.Warehouse',
        null=False,
        blank=False,
        verbose_name='仓库',
        related_name='zones',
        help_text="区域所属的仓库"
    )

    usage = models.CharField(
        '用途',
        null=False,
        blank=False,
        choices=LAYOUT_USAGE,
        max_length=30,
        default='container',
        help_text="区域的用途"
    )

    root_location = ActiveLimitForeignKey(
        'stock.Location',
        null=True,
        blank=True,
        verbose_name='根节点',
        related_name='self_zone',
        help_text="代表区域本身的根库位"
    )

    def __str__(self):
        return str(self.warehouse) + '/' + self.usage

    class Meta:
        verbose_name = '区域'
        verbose_name_plural = '区域'
        unique_together = (
            ('warehouse', 'usage'),
        )

    class States(BaseModel.States):
        active = Statement(
            Q(warehouse__is_active=True) & Q(warehouse__is_delete=False),
            inherits=BaseModel.States.active
        )
        stock = Statement(inherits=active, usage='stock')
        pick = Statement(inherits=active, usage='pick')
        check = Statement(inherits=active, usage='check')
        pack = Statement(inherits=active, usage='pack')
        wait = Statement(inherits=active, usage='wait')
        deliver = Statement(inherits=active, usage='deliver')
        customer = Statement(inherits=active, usage='customer')
        supplier = Statement(inherits=active, usage='supplier')
        produce = Statement(inherits=active, usage='produce')
        repair = Statement(inherits=active, usage='repair')
        scrap = Statement(inherits=active, usage='scrap')
        closeout = Statement(inherits=active, usage='closeout')
        initial = Statement(inherits=active, usage='initial')
        midway = Statement(inherits=active, usage='midway')
        USAGE_STATES = {
            'stock': stock,
            'pick': pick,
            'check': check,
            'pack': pack,
            'wait': wait,
            'deliver': deliver,
            'customer': customer,
            'supplier': supplier,
            'produce': produce,
            'repair': repair,
            'scrap': scrap,
            'closeout': closeout,
            'initial': initial,
            'midway': midway
        }

    def get_product_quantity(self, product):
        '''获得区域指定产品的数量'''
        return self.root_location.get_product_quantity(product)


class Location(BaseModel, TreeModel):
    '''库位'''

    zone = ActiveLimitForeignKey(
        'stock.Zone',
        null=False,
        blank=False,
        verbose_name='区域',
        related_name='locations',
        help_text="库位所属的区域"
    )

    parent_node = ActiveLimitForeignKey(
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

    class States(BaseModel.States):
        active = Statement(
            (
                Q(zone__is_delete=False) &
                Q(zone__is_active=True) &
                Q(zone__warehouse__is_delete=False) &
                Q(zone__warehouse__is_active=True)
            ),
            inherits=BaseModel.States.active
        )
        virtual = Statement(inherits=active, is_virtual=True)
        no_virtual = Statement(inherits=active, is_virtual=False)
        root = Statement(inherits=virtual, parent_node=None)

    def change_parent_node(self, node):
        '''判断上级库位是否为虚拟库位'''
        if node.check_states('virtual') and self.check_states('active') and self.zone == node.zone:
            return super(Location, self).change_parent_node(node.id)
        raise ValueError('上级库位必须为虚拟库位,且当前库位和新的上级库位必须在同一个区域内')

    @property
    def leaf_child_nodes(self):
        '''获得所有叶子节点'''
        return self.__class__.get_state_queryset('no_virtual', self.all_child_nodes)

    @property
    def cache(self):
        return CacheLocation(location=self)

    def in_sum(self, product):
        '''获取指定产品在库位的移入数量'''
        from django.db.models import Sum
        return Move.get_state_queryset('done').filter(
            to_location=self,
            procurement_detail_setting__detail__product=product
        ).aggregate(in_sum=Sum('quantity'))['in_sum'] or D('0')

    def out_sum(self, product):
        '''获取指定产品的库位的移出数量'''
        from django.db.models import Sum
        return Move.get_state_queryset('done').filter(
            from_location=self,
            procurement_detail_setting__detail__product=product
        ).aggregate(out_sum=Sum('quantity'))['out_sum'] or D('0')

    def get_lock_product_quantity(self,product):
        redis = Redis()
        return D(redis.zscore(self.cache.cache_name,'product_lock_{}'.format(product.pk)))

    def get_product_quantity(self, product):
        '''获取指定产品的数量'''
        redis = Redis()
        product_field = 'product_{}'.format(product.pk)
        product_lock_field = 'product_lock_{}'.format(product.pk)
        if self.check_states('virtual'):
            keys = [node.cache.cache_name for node in self.leaf_child_nodes]
            return D(redis.zinterstore(
                dest=(product_field,product_lock_field),
                keys=keys
            ))
        elif self.check_states('no_virtual'):
            return D(redis.zscore(
                self.cache.cache_name,
                product_field
            ) or '0') + D(redis.zscore(
                self.cache.cache_name,
                product_lock_field
            ) or '0')
        else:
            return D('0')


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
        'stock.ProcurementFromLocationSetting',
        null=False,
        blank=False,
        verbose_name='需求明细设置',
        related_name='moves',
        help_text="生成该移动的需求明细设置"
    )

    route_path_sort_setting = models.ForeignKey(
        'stock.RoutePathSortSetting',
        null=False,
        blank=False,
        verbose_name='需求匹配路径设置',
        related_name='moves',
        help_text="生成该移动的路线路径"
    )

    quantity = QuantityField(
        '移动数量',
        null=False,
        blank=False,
        uom='procurement_detail_setting.detail.product.template.uom',
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

    class States(BaseModel.States):
        active = BaseModel.States.active
        draft = Statement(inherits=active, state='draft')
        confirmed = Statement(inherits=active, state='confirmed')
        done = Statement(inherits=active, state='done')

    @property
    def product(self):
        return self.procurement_detail_setting.detail.product

    def refresh_lock_product_quantity(self):
        return self.from_location.cache.lock(
            product=self.product,
            quantity=self.quantity
        )

    def refresh_product_quantity(self):
        redis = Redis()
        pipe = redis.pipeline()
        product = self.product
        self.from_location.cache.refresh(
            product=product,
            quantity=(-self.quantity),
            pipe=pipe
        )
        self.to_location.cache.refresh(
            product=product,
            quantity=self.quantity,
            pipe=pipe
        )
        self.from_location.cache.lock(product,-self.quantity,pipe=pipe)
        if self.from_location.zone.usage != self.to_location.zone.usage:
            product.cache.refresh(self.from_location.zone.usage, -self.quantity, pipe=pipe)
            product.cache.refresh(self.to_location.zone.usage, self.quantity, pipe=pipe)
        pipe.execute()

    def confirm(self):
        if self.check_to_set_state('draft',set_state='confirmed'):
            self.refresh_lock_product_quantity()
            return True
        return False

    def done(self):
        if self.check_to_set_state('confirmed',set_state='done'):
            self.refresh_product_quantity()
            return True
        return False


# class PickOrder(StockOrder):
#     '''分拣表单'''
#     pass
#
# class CheckOrder(StockOrder):
#     '''送检表单'''
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
# class OutPutOrder(StockOrder):
#     '''出库表单'''
#     pass
#
# class InPutOrder(StockOrder):
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
        unique=True,
        max_length=190,
        help_text="路线的名称"
    )

    warehouse = ActiveLimitForeignKey(
        'stock.Warehouse',
        verbose_name='仓库',
        related_name='routes',
        help_text="路线所属的仓库"
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
        through='stock.RoutePathSortSetting',
        through_fields=('route','path'),
        blank=False,
        verbose_name='路径',
        related_name='routes',
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

    class States(BaseModel.States):
        active = BaseModel.States.active
        direct = Statement(inherits=active, return_method='direct')
        fallback = Statement(inherits=active, return_method='fallback')
        config = Statement(
            Q(return_route__isnull=False),
            inherits=active,
            return_method='config'
        )


class RoutePathSortSetting(models.Model):
    '''路线的路径配置'''
    route = ActiveLimitForeignKey(
        'stock.Route',
        null=False,
        blank=False,
        verbose_name='路线',
        related_name='route_path_sort_settings',
        help_text="路径设置所属的路线"
    )

    path = ActiveLimitForeignKey(
        'stock.Path',
        null=False,
        blank=False,
        verbose_name='路径',
        related_name='route_path_sort_settings',
        help_text="路径设置所设置的路径"
    )

    sequence = models.PositiveSmallIntegerField(
        '排序',
        null=False,
        blank=False,
        default=0,
        help_text="路径设置的排序"
    )

    class Meta:
        verbose_name = '路线的路径配置'
        verbose_name_plural = '路线的路径配置'
        unique_together = ('route','path','sequence')
        ordering = ('sequence',)


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
        uom='product.template.uom',
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
        editable=False,
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
        uom='product.template.uom',
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


class PackageNode(TreeModel,StateMachine):
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
        help_text="该节点的父节点"
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

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '包裹节点'
        verbose_name_plural = '包裹节点'
        unique_together = (
            ('parent_node', 'template'),
        )



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

    class States(BaseModel.States):
        active = BaseModel.States.active
        draft = Statement(inherits=active,state='draft')
        confirmed = Statement(inherits=active,state='confirmed')
        done = Statement(inherits=active,state='done')

    def confirm(self):
        '''判断'''
        with transaction.atomic():
            if self.check_states('draft'):
                self.set_state('confirmed')
                return True
            return False


class ProcurementDetail(BaseModel):
    '''需求明细'''
    from_locations = models.ManyToManyField(
        'stock.Location',
        blank=False,
        through='stock.ProcurementFromLocationSetting',
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
            ProcurementFromLocationSetting.objects.filter(
                detail=self).values_list('quantity', flat=True)
        )


class ProcurementFromLocationSetting(models.Model):
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
        uom='product.template.uom',
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

    @property
    def moving(self):
        '''获得当前需求来源位置正在执行的移动'''
        return Move.get_state_instance('confirmed',self.moves.all())


