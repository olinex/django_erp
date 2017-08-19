#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from decimal import Decimal as D

from django.conf import settings
from django.db import transaction
from django.db.models import Q, F

from apps.djangoperm import models
from .utils import LocationForeignKey
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from apps.product.models import Assembly, Product
from apps.account.utils import PartnerForeignKey
from apps.product.utils import QuantityField
from common import Redis
from common.abstractModel import BaseModel, TreeModel
from common.fields import (
    ActiveLimitForeignKey,
    ActiveLimitOneToOneField,
    SimpleStateCharField, CancelableSimpleStateCharField
)
from common.state import Statement, StateMachine


class CacheItem(object):
    '''产品的缓存对象'''
    ALL = {'stock', 'pick', 'check', 'pack', 'wait', 'deliver', 'midway'}
    SETTLED = {'customer', 'repair'}
    TRANSPORTING = {'pick', 'check', 'pack', 'wait', 'deliver', 'midway'}

    def __init__(self, item):
        self.item = item

    @property
    def cache_name(self):
        return 'item_{}'.format(self.item.pk)

    def get_quantity(self, usages):
        redis = Redis()
        usage_list = set(Zone.States.USAGE_STATES.keys())
        if isinstance(usages, (set,)) and not usages.difference(usage_list):
            return sum(
                D(redis.zscore(self.cache_name, usage)) for usage in usages
            )
        elif usages in usage_list:
            return D(redis.zscore(self.cache_name, usages))

    @property
    def all(self):
        return self.get_quantity(self.ALL)

    @property
    def settled(self):
        return self.get_quantity(self.SETTLED)

    @property
    def transporting(self):
        return self.get_quantity(self.TRANSPORTING)

    def refresh(self, field, quantity, pipe=None):
        '''更新字段数量'''
        if field in Zone.States.USAGE_STATES.keys():
            redis = pipe or Redis()
            return redis.zincrby(self.cache_name, field, quantity)
        raise AttributeError('错误的字段类型名称')

    def sync(self):
        '''同步所有的仓库的产品数量'''
        redis = Redis()
        pipe = redis.pipeline()
        watch_keys = Warehouse.leaf_child_locations_cache_name
        pipe.watch(watch_keys)
        pipe.delete(self.cache_name)
        for warehouse in Warehouse.get_state_queryset('active'):
            for usage in Zone.States.USAGE_STATES.keys():
                quantity = warehouse.get_item_quantity(
                    item=self.item,
                    usage=usage,
                )
                pipe.zincrby(self.cache_name, usage, quantity)
        pipe.execute()


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

    @staticmethod
    def item_name(item):
        return 'item_{}'.format(item.pk)

    @staticmethod
    def item_lock_name(item):
        return 'item_lock_{}'.format(item.pk)

    def refresh(self, item, quantity, pipe=None):
        redis = pipe or Redis()
        redis.zincrby(self.cache_name, self.item_name(item), quantity)

    def lock(self, item, quantity, pipe=None):
        redis = pipe or Redis()
        redis.zincrby(self.cache_name, self.item_lock_name(item), -quantity)

    def free_all(self, item, pipe=None):
        redis = pipe or Redis()
        redis.zrem(self.cache_name, self.item_lock_name(item))

    def sync(self):
        '''同步库存的产品数量'''
        if self.location.check_states('no_virtual'):
            redis = Redis()
            pipe = redis.pipeline()
            pipe.delete(self.cache_name)
            for item in set(move.item for move in Move.get_state_queryset('done')):
                self.refresh(
                    item,
                    self.location.in_sum(item) - self.location.out_sum(item),
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

    def get_item_quantity(self, item, usage='all'):
        if usage in Zone.States.USAGE_STATES.keys():
            zone = Zone.get_state_queryset(usage, self.zones.all())[0]
            return zone.get_item_quantity(item)
        elif usage == 'all':
            redis = Redis()
            return D(redis.zinterstore(
                dest=('item_{}'.format(item.pk),),
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

    def get_item_quantity(self, item):
        '''获得区域指定产品的数量'''
        return self.root_location.get_item_quantity(item)


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
            return super(Location, self).change_parent_node(node)
        raise ValueError('上级库位必须为虚拟库位,且当前库位和新的上级库位必须在同一个区域内')

    @property
    def leaf_child_nodes(self):
        '''获得所有叶子节点'''
        return self.__class__.get_state_queryset('no_virtual', self.all_child_nodes)

    @property
    def cache(self):
        if not hasattr(self, '_cache'):
            self._cache = CacheLocation(location=self)
        return self._cache

    def in_sum(self, item):
        '''获取指定产品在库位的移入数量'''
        from django.db.models import Sum
        return Move.get_state_queryset('done').filter(
            to_location=self,
            procurement_detail_setting__detail__item=item
        ).aggregate(in_sum=Sum('quantity'))['in_sum'] or D('0')

    def out_sum(self, item):
        '''获取指定产品的库位的移出数量'''
        from django.db.models import Sum
        return Move.get_state_queryset('done').filter(
            from_location=self,
            procurement_detail_setting__detail__item=item
        ).aggregate(out_sum=Sum('quantity'))['out_sum'] or D('0')

    def get_lock_item_quantity(self, item):
        redis = Redis()
        return D(redis.zscore(self.cache.cache_name, self.cache.item_lock_name(item)))

    def get_item_quantity(self, item):
        '''获取指定产品的数量'''
        redis = Redis()
        item_field = self.cache.item_name(item)
        item_lock_field = self.cache.item_lock_name(item)
        if self.check_states('virtual'):
            keys = [node.cache.cache_name for node in self.leaf_child_nodes]
            return D(redis.zinterstore(
                dest=(item_field, item_lock_field),
                keys=keys
            ))
        elif self.check_states('no_virtual'):
            return D(redis.zscore(
                self.cache.cache_name,
                item_field
            ) or '0') + D(redis.zscore(
                self.cache.cache_name,
                item_lock_field
            ) or '0')
        else:
            return D('0')


class Package(BaseModel):
    '''包裹记录'''
    root_node = models.ForeignKey(
        'stock.PackageNode',
        null=False,
        blank=False,
        verbose_name='包裹树',
    )


class Move(BaseModel):
    '''移动'''

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

    to_moves = models.ManyToManyField(
        'self',
        blank=True,
        verbose_name='后续移动',
        related_name='from_moves',
        help_text="计划移动链的后续移动"
    )

    procurement_details = models.ManyToManyField(
        'stock.ProcurementDetail',
        blank=False,
        verbose_name='需求明细',
        related_name='moves',
        help_text="生成该移动的需求明细"
    )

    item = ActiveLimitForeignKey(
        'stock.Item',
        null=False,
        blank=False,
        verbose_name='移库元素',
        related_name='moves',
        help_text="进行移库的元素"
    )

    route_zone_setting = models.ForeignKey(
        'stock.RouteZoneSetting',
        null=False,
        blank=False,
        verbose_name='需求匹配区域设置',
        related_name='moves',
        help_text="生成该移动的路线区域"
    )

    quantity = QuantityField(
        '移动数量',
        null=False,
        blank=False,
        uom='item.instance.uom',
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
        unique_together = ('item', 'route_zone_setting')

    class States(BaseModel.States):
        active = BaseModel.States.active
        draft = Statement(inherits=active, state='draft')
        confirmed = Statement(inherits=active, state='confirmed')
        doing = Statement(Q(state='draft') | Q(state='confirmed'), inherits=active)
        done = Statement(inherits=active, state='done')

    def refresh_lock_item_quantity(self):
        return self.from_location.cache.lock(
            item=self.item,
            quantity=self.quantity
        )

    def refresh_item_quantity(self):
        redis = Redis()
        pipe = redis.pipeline()
        self.from_location.cache.refresh(
            item=self.item,
            quantity=(-self.quantity),
            pipe=pipe
        )
        self.to_location.cache.refresh(
            item=self.item,
            quantity=self.quantity,
            pipe=pipe
        )
        self.from_location.cache.lock(self.item, -self.quantity, pipe=pipe)
        if self.from_location.zone.usage != self.to_location.zone.usage:
            self.item.cache.refresh(self.from_location.zone.usage, -self.quantity, pipe=pipe)
            self.item.cache.refresh(self.to_location.zone.usage, self.quantity, pipe=pipe)
        pipe.execute()

    def confirm(self):
        if self.check_to_set_state('draft', set_state='confirmed'):
            self.refresh_lock_item_quantity()
            return True
        return False

    def done(self, next_location=None):
        with transaction.atomic():
            procurement = self.procurement_details.first().procurement
            next_route_zone_setting = procurement.route.next_route_zone_setting(
                now_route_zone_setting=self.route_zone_setting
            )
            if (((
                     not next_route_zone_setting and not next_location) or next_location.zone == next_route_zone_setting.zone) and
                    self.check_to_set_state('confirmed', set_state='done')):
                self.refresh_item_quantity()
                if not procurement.check_states('cancel'):
                    if next_route_zone_setting:
                        next_move = Move.objects.create(
                            from_location=self.to_location,
                            to_location=next_location,
                            route_zone_setting=next_route_zone_setting,
                            item=self.item,
                            quantity=self.quantity,
                            state='draft'
                        )
                        next_move.procurement_details.set(self.procurement_details.all())
                        self.to_moves.add(next_move)
                        self.save()
                    elif Move.check_state_queryset('done',
                                                   Move.objects.filter(procurement_details__procurement=procurement)):
                        procurement.set_state('done')
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


class Route(BaseModel):
    '''路线'''

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

    initial_zone = ActiveLimitForeignKey(
        'stock.Zone',
        null=True,
        blank=True,
        verbose_name='起始区域',
        related_name='initial_routes',
        help_text="路线的起始区域"
    )

    end_zone = ActiveLimitForeignKey(
        'stock.Zone',
        null=True,
        blank=True,
        verbose_name='终点区域',
        related_name='end_routes',
        help_text="路线的终点区域"
    )

    zones = models.ManyToManyField(
        'stock.Zone',
        through='stock.RouteZoneSetting',
        through_fields=('route', 'zone'),
        blank=False,
        verbose_name='区域',
        related_name='routes',
        help_text="路线的详细路径区域"
    )

    users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=False,
        verbose_name='用户',
        related_name='usable_routes',
        help_text='可执行该路线调拨的用户'
    )

    sequence = models.PositiveSmallIntegerField(
        '优先级',
        null=False,
        blank=False,
        default=0,
        help_text="在相同起始库位和终点库位的路线的优先级"
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '路线'
        verbose_name_plural = '路线'
        unique_together = ('initial_zone', 'end_zone', 'sequence')

    class States(BaseModel.States):
        active = BaseModel.States.active

    @property
    def direct_path(self):
        return (self.initial_zone, self.end_zone)

    def next_route_zone_setting(self, now_route_zone_setting=None):
        if now_route_zone_setting:
            return RouteZoneSetting.objects.filter(
                route=self,
                sequence__gt=now_route_zone_setting.sequence
            ).first()
        return RouteZoneSetting.objects.filter(
            route=self
        )[1]


class RouteZoneSetting(models.Model):
    '''路线的路径配置'''
    RELATED_NAME = 'route_zone_settings'

    route = ActiveLimitForeignKey(
        'stock.Route',
        null=False,
        blank=False,
        verbose_name='路线',
        related_name=RELATED_NAME,
        help_text="路径设置所属的路线"
    )

    zone = ActiveLimitForeignKey(
        'stock.Zone',
        null=False,
        blank=False,
        verbose_name='区域',
        related_name=RELATED_NAME,
        help_text="路径设置所设置的区域"
    )

    sequence = models.PositiveSmallIntegerField(
        '排序',
        null=False,
        blank=False,
        default=0,
        help_text="路径设置的排序"
    )

    def __str__(self):
        return '{}/{}/{}'.format(self.route, self.zone, self.sequence)

    class Meta:
        verbose_name = '路线的路径区域配置'
        verbose_name_plural = '路线的路径配置'
        unique_together = ('zone', 'sequence')
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

    items = models.ManyToManyField(
        'stock.Item',
        blank=False,
        through='stock.PackageTypeItemSetting',
        through_fields=('package_type', 'item'),
        verbose_name='产品分类',
        related_name='package_types',
        help_text="包裹可包装的元素类型"
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '包裹类型'
        verbose_name_plural = '包裹类型'


class PackageTypeItemSetting(models.Model):
    '''包裹类型产品分类设置'''
    RELATED_NAME = 'item_settings'

    package_type = ActiveLimitForeignKey(
        'stock.PackageType',
        null=False,
        blank=False,
        verbose_name='包裹类型',
        related_name=RELATED_NAME,
        help_text="相关的包裹类型"
    )

    item = ActiveLimitForeignKey(
        'stock.Item',
        null=False,
        blank=False,
        verbose_name='元素类型',
        related_name=RELATED_NAME,
        help_text="相关的元素的类型"
    )

    max_quantity = QuantityField(
        '最大数量',
        null=False,
        blank=False,
        uom='item.instance.uom',
        help_text="包裹类型能够包含该产品的最大数量"
    )

    def __str__(self):
        return '{}-{}({})'.format(
            self.package_type,
            self.item,
            str(self.max_quantity)
        )

    class Meta:
        verbose_name = '包裹类型设置'
        verbose_name_plural = '包裹类型设置'
        unique_together = (
            ('package_type', 'item'),
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

    type_settings = models.ManyToManyField(
        'stock.PackageTypeItemSetting',
        blank=False,
        through='stock.PackageTemplateItemSetting',
        through_fields=('package_template', 'type_setting'),
        verbose_name='产品分类设置',
        related_name='package_templates',
        help_text="包裹可包装的产品分类"
    )

    def __str__(self):
        return str(self.package_type)

    class Meta:
        verbose_name = '包裹模板'
        verbose_name_plural = '包裹模板'


class PackageTemplateItemSetting(models.Model):
    '''包裹模板产品设置'''
    RELATED_NAME = 'template_settings'

    package_template = ActiveLimitForeignKey(
        'stock.PackageTemplate',
        null=False,
        blank=False,
        verbose_name='包裹模板',
        related_name=RELATED_NAME,
        help_text="相关的包裹模板"
    )

    type_setting = models.ForeignKey(
        'stock.PackageTypeItemSetting',
        null=False,
        blank=False,
        verbose_name='包裹类型设置',
        related_name=RELATED_NAME,
        help_text="包裹模板明细遵循的包裹类型"
    )

    quantity = QuantityField(
        '最大数量',
        null=False,
        blank=False,
        uom='type_setting.uom',
        help_text="包裹模板包含该产品的数量"
    )

    def __str__(self):
        return '{}-{}({})'.format(
            self.package_template,
            self.type_setting,
            str(self.quantity)
        )

    class Meta:
        verbose_name = '包裹模板产品设置'
        verbose_name_plural = '包裹模板产品设置'
        unique_together = (
            ('package_template', 'type_setting'),
        )


class PackageNode(TreeModel, StateMachine):
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

    items = GenericRelation('stock.Item')

    @property
    def item(self):
        return self.items.first()

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

    user = PartnerForeignKey(
        null=False,
        blank=False,
        verbose_name='合作伙伴',
        help_text="提出需求的相关合作伙伴"
    )

    address = ActiveLimitForeignKey(
        'account.Address',
        null=False,
        blank=False,
        verbose_name='送货地址',
        related_name='procurements',
        help_text="客户要求到达的送货地址"
    )

    is_return = models.BooleanField(
        '退货状态',
        default=False,
        help_text="需求的退货状态,若改需求为退货需求,则为True"
    )

    return_procurement = ActiveLimitOneToOneField(
        'self',
        null=True,
        blank=True,
        verbose_name='退货需求',
        related_name='origin_procurement',
        help_text="产生退货时,需求对应的退货需求"
    )

    route = ActiveLimitForeignKey(
        'stock.Route',
        null=False,
        blank=False,
        verbose_name='路线',
        related_name='procurements',
        help_text="根据需求产生的位置以及指定的产品来源库位自动匹配的移动路线"
    )

    state = CancelableSimpleStateCharField(
        '状态',
        help_text="需求单的状态"
    )

    def __str__(self):
        return '{}-{}'.format(str(self.user), str(self.route))

    class Meta:
        verbose_name = '需求'
        verbose_name_plural = '需求'

    class States(BaseModel.States):
        active = BaseModel.States.active
        draft = Statement(inherits=active, state='draft')
        confirmed = Statement(inherits=active, state='confirmed')
        done = Statement(inherits=active, state='done')
        cancelable = Statement(inherits=confirmed, is_return=False)
        cancel = Statement(inherits=active, state='cancel')

    def confirm(self):
        with transaction.atomic():
            next_zone_setting = self.route.next_route_zone_setting()
            if (not self.details.exclude(
                        Q(from_location__zone=F('procurement__route__initial_zone')) &
                        Q(next_location__zone=next_zone_setting.zone)).exists() and
                    self.check_states('draft')):
                details = self.details.all()
                self.set_state('confirmed')
                for detail in details:
                    move = detail.get_first_move(first_route_zone_setting=next_zone_setting)
                    move.save()
                    move.procurement_details.add(detail)
                return True
            return False


class ProcurementDetail(models.Model):
    '''需求明细'''

    from_location = LocationForeignKey(
        null=False,
        blank=False,
        verbose_name='来源库位',
        related_name='first_move_procurement_details',
        help_text="产品来源的库位"
    )

    next_location = LocationForeignKey(
        null=False,
        blank=False,
        verbose_name='下一步库位',
        related_name='second_move_procurement_details',
        help_text="产品第一步需要移动至的库位"
    )

    item = ActiveLimitForeignKey(
        'stock.Item',
        null=False,
        blank=False,
        verbose_name='产品',
        help_text="明细相关的产品"
    )

    quantity = QuantityField(
        '数量',
        null=False,
        blank=False,
        uom='product.template.uom',
        help_text="产品的数量"
    )

    procurement = ActiveLimitForeignKey(
        'stock.Procurement',
        null=False,
        blank=False,
        verbose_name='需求',
        related_name='details',
        help_text="需求明细所属的需求"
    )

    def __str__(self):
        return '{}/{}'.format(str(self.procurement), str(self.item))

    class Meta:
        verbose_name = "需求明细"
        verbose_name_plural = "需求明细"
        unique_together = ('procurement', 'item')

    @property
    def moving(self):
        '''获得当前与需求明细相关的进行中的移动'''
        moves = Move.get_state_queryset('doing', self.moves.all())
        moves_count = moves.count()
        if moves_count == 1:
            return moves[0]
        elif moves_count == 0:
            return None
        else:
            raise ValueError('同一需求明细下不能存在多个进行中的移动')

    def get_first_move(self, first_route_zone_setting):
        return Move(
            from_location=self.from_location,
            to_location=self.next_location,
            route_zone_setting=first_route_zone_setting,
            quantity=self.quantity,
            item=self.item,
            state='draft'
        )


class Item(BaseModel, StateMachine):
    '''移库元素'''

    content_type = models.ForeignKey(
        ContentType,
        null=False,
        blank=False,
        verbose_name='类型',
        related_name='item',
        help_text="移库单位的类型"
    )

    object_id = models.PositiveIntegerField(
        '元素ID',
        null=False,
        blank=False,
        help_text="移库单位对应对象的id"
    )

    instance = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return str(self.instance)

    class Meta:
        verbose_name = '移库元素'
        verbose_name_plural = '移库元素'
        unique_together = ('content_type', 'object_id')

    class States(BaseModel.States):
        active = BaseModel.States.active
        product = Statement(
            Q(content_type=ContentType.objects.get_for_model(Product)),
            inherits=active
        )
        assembly = Statement(
            Q(content_type=ContentType.objects.get_for_model(Assembly)),
            inherits=active
        )
        package_node = Statement(
            Q(content_type=ContentType.objects.get_for_model(PackageNode)),
            inherits=active
        )

    @property
    def cache(self):
        return CacheItem(self)
