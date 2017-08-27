#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from decimal import Decimal as D

from django.conf import settings
from django.db import transaction
from django.db.models import Q, F
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation

from apps.djangoperm import models
from .utils import LocationForeignKey
from apps.product.models import Product
from apps.account.utils import PartnerForeignKey
from apps.product.utils import QuantityField
from common import Redis
from common.abstractModel import BaseModel, TreeModel
from common.exceptions import NotInStates
from common.fields import (
    ActiveLimitForeignKey,
    ActiveLimitOneToOneField,
    SimpleStateCharField,
    CancelableSimpleStateCharField
)
from common.state import Statement, StateMachine


class CacheItem(object):
    '''
    object reflect to stock item.
    as a manager which have all methods to control the quantity of item
    '''
    ALL = {'stock', 'pick', 'check', 'pack', 'wait', 'deliver', 'midway'}
    SETTLED = {'customer', 'repair'}
    TRANSPORTING = {'pick', 'check', 'pack', 'wait', 'deliver', 'midway'}

    ITEM_NAME_TEMPLATE = 'zone_{}_item_{}'
    ITEM_LOCK_NAME_TEMPLATE = 'lock_zone_{}_item_{}'

    def __init__(self, zone, item):
        '''
        :param zone: stock.Zone instance
        :param item: stock.Item instance
        '''
        self.zone = zone
        self.item = item

    @classmethod
    def item_name(cls, zone, item):
        '''
        class method will return the key of item of zone
        :param zone: stock.Zone instance
        :param item: stock.Item instance
        :return: string
        '''
        return cls.ITEM_NAME_TEMPLATE.format(zone.pk, item.pk)

    @classmethod
    def item_lock_name(cls, zone, item):
        '''
        class method will return the lock key of item of zone
        :param zone: stock.Zone instance
        :param item: stock.Item instance
        :return: string
        '''
        return cls.ITEM_LOCK_NAME_TEMPLATE.format(zone.pk, item.pk)

    @property
    def cache_name(self):
        '''
        the name for redis as the key,each warehouse has it own cache name
        :return: string
        '''
        return self.item_name(self.zone,self.item)

    def get_quantity(self, usages):
        '''
        sum of item quantities figure out by set of usage
        :param usages: set or string
        :return: decimal
        '''
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
        '''
        sum of item in all zones
        :return: decimal
        '''
        return self.get_quantity(self.ALL)

    @property
    def settled(self):
        '''
        sum of item in settled zones
        :return: decimal
        '''
        return self.get_quantity(self.SETTLED)

    @property
    def transporting(self):
        '''
        sum of item in transporting zones
        :return: decimal
        '''
        return self.get_quantity(self.TRANSPORTING)

    def refresh(self, usage, quantity, pipe=None):
        '''
        increase of decrease the quantity of item in the zone of usage
        :param usage: string
        :param quantity: decimal
        :param pipe: pipeline of redis
        :return: 0 or 1
        '''
        if usage in Zone.States.USAGE_STATES.keys():
            redis = pipe or Redis()
            return redis.zincrby(self.cache_name, usage, quantity)
        raise AttributeError(usage + _(' is unknown usage of zone.'))

    def sync(self):
        '''
        refresh all zones item quantity in the warehouse
        :return: None
        '''
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
    '''
    object reflect to stock location.
    as a manager which have all methods to control the quantity of item in the location
    '''
    LOCATION_NAME_TEMPLATE = 'location_{}'

    def __init__(self, location):
        '''
        :param location: stock.Location instance
        '''
        self.location = location

    @property
    def cache_name(self):
        '''
        the name of location in redis as key
        :return: string
        '''
        return self.LOCATION_NAME_TEMPLATE.format(self.location.pk)

    def refresh(self, item, quantity, pipe=None):
        '''
        increase of decrease the quantity of item in the location
        :param item: stock.Item instance
        :param quantity: decimal
        :param pipe: redis pipeline
        :return: 0 or 1
        '''
        redis = pipe or Redis()
        return redis.zincrby(
            self.cache_name,
            CacheItem.item_name(self.location.zone,item),
            quantity
        )

    def lock(self, item, quantity, pipe=None):
        '''
        increase of decrease the lock quantity of item in the location
        :param item: stock.Item instance
        :param quantity: decimal
        :param pipe: redis pipline
        :return: 0 or 1
        '''
        redis = pipe or Redis()
        return redis.zincrby(
            self.cache_name,
            CacheItem.item_lock_name(self.location.zone, item),
            -quantity
        )

    def free_all(self, item, pipe=None):
        '''
        delete the item score from location
        :param item: stock.Item instance
        :param pipe: redis pipeline
        :return: 0 or 1
        '''
        redis = pipe or Redis()
        return redis.zrem(
            self.cache_name,
            CacheItem.item_lock_name(self.location.zone, item)
        )

    def sync(self):
        '''
        refresh all item quantity in the location
        :return: None
        '''
        self.location.check_states('no_virtual', raise_exception=True)
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


class PackageType(BaseModel):
    '''
    the type of package which define it name,the name must be unique
    '''

    name = models.CharField(
        _('name'),
        null=False,
        blank=False,
        unique=True,
        max_length=90,
        help_text=_("the type name of package")
    )

    items = models.ManyToManyField(
        'stock.Item',
        blank=False,
        through='stock.PackageTypeItemSetting',
        through_fields=('package_type', 'item'),
        verbose_name=_('items'),
        related_name='package_types',
        help_text=_('the packable items of package')
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('package type')
        verbose_name_plural = _('package types')


class PackageTypeItemSetting(models.Model, StateMachine):
    '''
    Constraint sets the maximum number of packages
    '''
    RELATED_NAME = 'item_settings'

    package_type = ActiveLimitForeignKey(
        'stock.PackageType',
        null=False,
        blank=False,
        verbose_name=_('package type'),
        related_name=RELATED_NAME,
        help_text=_('the type of package which settings belongs to')
    )

    item = ActiveLimitForeignKey(
        'stock.Item',
        null=False,
        blank=False,
        verbose_name=_('item'),
        related_name=RELATED_NAME,
        help_text=_('the item which can be packed in this type of package')
    )

    max_quantity = QuantityField(
        _('max quantity'),
        null=False,
        blank=False,
        uom='item.instance.uom',
        help_text=_('the max quantity of item can be packed into package')
    )

    def __str__(self):
        return '{}-{}({})'.format(
            self.package_type,
            self.item,
            str(self.max_quantity)
        )

    class Meta:
        verbose_name = _('item setting of package type')
        verbose_name_plural = _('item settings of package type')
        unique_together = (
            ('package_type', 'item'),
        )

    class States:
        product_setting = Statement(
            Q(item__content_type__app_label='product') &
            Q(item__content_type__model='Product')
        )


class PackageTemplate(BaseModel):
    '''
    the template of package type
    '''
    name = models.CharField(
        _('name'),
        null=False,
        blank=False,
        unique=True,
        max_length=90,
        help_text=_('the name of package template')
    )

    package_type = ActiveLimitForeignKey(
        'stock.PackageType',
        null=False,
        blank=False,
        verbose_name=_('package type'),
        help_text=_('the package type of this template,constraint max number of item')
    )

    type_settings = models.ManyToManyField(
        'stock.PackageTypeItemSetting',
        blank=False,
        through='stock.PackageTemplateItemSetting',
        through_fields=('package_template', 'type_setting'),
        verbose_name=_('the type settings of package'),
        related_name='package_templates',
        help_text=_('the type settings of package which constraint max number of item')
    )

    def __str__(self):
        return str(self.package_type)

    class Meta:
        verbose_name = _('package template')
        verbose_name_plural = _('package tempaltes')


class PackageTemplateItemSetting(models.Model):
    '''
    the setting which set the number of item in the package
    '''
    RELATED_NAME = 'template_settings'

    package_template = ActiveLimitForeignKey(
        'stock.PackageTemplate',
        null=False,
        blank=False,
        verbose_name=_('package template'),
        related_name=RELATED_NAME,
        help_text=_('the package template which setting belongs to')
    )

    type_setting = models.ForeignKey(
        'stock.PackageTypeItemSetting',
        null=False,
        blank=False,
        verbose_name=_('package type setting'),
        related_name=RELATED_NAME,
        help_text=_('the package type setting will constraint the max number of item of this template setting')
    )

    quantity = QuantityField(
        _('quantity'),
        null=False,
        blank=False,
        uom='type_setting.uom',
        help_text=_('the quantity of item in package tempalte')
    )

    def __str__(self):
        return '{}-{}({})'.format(
            self.package_template,
            self.type_setting,
            str(self.quantity)
        )

    class Meta:
        verbose_name = _('package template setting')
        verbose_name_plural = _('package template settings')
        unique_together = (
            ('package_template', 'type_setting'),
        )


class PackageNode(TreeModel):
    '''
    package node,every node contain an package template
    '''

    template = ActiveLimitForeignKey(
        'stock.PackageTemplate',
        null=False,
        blank=False,
        verbose_name=_('package template'),
        help_text=_('package template in the package tree')
    )

    items = GenericRelation('stock.Item')

    @property
    def item(self):
        '''
        get the relate item about itself,in the stock.Item,it constraint the ccontent type and instance id,
        so it must have the only one item
        :return: stock.Item instance
        '''
        return self.items.first()

    def __str__(self):
        return self.template.name

    class Meta:
        verbose_name = _('package node')
        verbose_name_plural = _('package nodes')
        unique_together = (
            ('parent_node', 'template'),
        )


class ProcurementOrder(BaseModel):
    '''abstract order about procurement'''

    procurement = ActiveLimitOneToOneField(
        'stock.Procurement',
        null=False,
        blank=False,
        verbose_name=_('procurement'),
        help_text=_('the procurement about this order')
    )

    class Meta:
        abstract = True


class ProcurementOrderDetail(BaseModel):
    '''abstract order detail about procurement detail'''
    procurement_detail = ActiveLimitForeignKey(
        'stock.ProcurementDetail',
        null=False,
        blank=False,
        verbose_name=_('procurement detail'),
        help_text=_('the procurementdetail baout this order line')
    )

    class Meta:
        abstract = True


class Warehouse(BaseModel):
    '''
    warehouse have different zones
    '''
    name = models.CharField(
        _('name'),
        null=False,
        blank=False,
        max_length=90,
        help_text=_('the name of warehouse')
    )

    manager = PartnerForeignKey(
        null=False,
        blank=False,
        verbose_name=_('partner manage user'),
        help_text=_('partner user can manage this warehouse')
    )

    address = ActiveLimitForeignKey(
        'account.Address',
        null=False,
        blank=False,
        verbose_name=_('address'),
        help_text=_('the real address of warehouse')
    )

    def get_default_location(self,usage):
        '''

        :param usage:
        :return:
        '''
        return Location.get_state_instance(
            'no_virtual',
            Location.objects.filter(
                parent_node=None,
                zone__warehouse=self,
                zone__usage=usage
            )
        )

    @property
    def initial_location(self):
        return self.get_default_location('initial')

    @property
    def scrap_location(self):
        return self.get_default_location('scrap')
    @property
    def closeout_location(self):
        return self.get_default_location('closeout')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '仓库'
        verbose_name_plural = '仓库'

    def create_zones(self):
        '''
        创建仓库下的各个区域
        :return:None
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
                    is_virtual=usage[0] not in Zone.INDIVISIBLE_USAGE,
                    x='', y='', z=''
                )
                zone.root_location = location
                zone.save()

    def create_default_routes(self):
        '''
        创建仓库下的默认路线
        :return: None
        '''
        with transaction.atomic():
            for route_type, explain in Route.ROUTE_TYPE:
                Route.objects.create(
                    warehouse=self,
                    name='default/{}/{}'.format(self, route_type),
                    route_type=route_type,
                    sequence=0
                )

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
            zone = Zone.get_state_queryset(usage, self.zones.all()).first()
            return zone.get_item_quantity(item)
        elif usage == 'all':
            redis = Redis()
            return D(redis.zinterstore(
                dest=('item_{}'.format(item.pk),),
                keys=[location.cache.cache_name for location in self.leaf_child_locations]
            ))
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

    INDIVISIBLE_USAGE = ('scrap', 'closeout', 'initial',)

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
        node.check_states('virtual', raise_exception=True)
        self.check_states('active', raise_exception=True)
        if self.zone == node.zone:
            return super(Location, self).change_parent_node(node)
        raise ValueError('当前库位和新的上级库位必须在同一个区域内')

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

    to_move = ActiveLimitOneToOneField(
        'self',
        null=True,
        blank=True,
        verbose_name='后续移动',
        related_name='from_moves',
        help_text="计划移动链的后续移动"
    )

    procurement_detail = models.ForeignKey(
        'stock.ProcurementDetail',
        blank=False,
        verbose_name='需求明细',
        related_name='moves',
        help_text="生成该移动的需求明细"
    )

    zone_setting = models.ForeignKey(
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

    is_return = models.BooleanField(
        '退货状态',
        default=False,
        help_text="移动的状态,False为退货状态"
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
        unique_together = ('procurement_detail', 'zone_setting', 'is_return')

    class States(BaseModel.States):
        active = BaseModel.States.active
        draft = Statement(inherits=active, state='draft')
        confirmed = Statement(inherits=active, state='confirmed')
        doing = Statement(Q(state='draft') | Q(state='confirmed'), inherits=active)
        done = Statement(inherits=active, state='done')
        is_return = Statement(inherits=active, is_return=True)
        no_return = Statement(inherits=active, is_return=False)

    def refresh_lock_item_quantity(self):
        return self.from_location.cache.lock(
            item=self.procurement_detail.item,
            quantity=self.quantity
        )

    def refresh_item_quantity(self):
        redis = Redis()
        pipe = redis.pipeline()
        self.from_location.cache.refresh(
            item=self.procurement_detail.item,
            quantity=(-self.quantity),
            pipe=pipe
        )
        self.to_location.cache.refresh(
            item=self.procurement_detail.item,
            quantity=self.quantity,
            pipe=pipe
        )
        self.from_location.cache.lock(self.procurement_detail.item, -self.quantity, pipe=pipe)
        if self.from_location.zone.usage != self.to_location.zone.usage:
            self.procurement_detail.item.cache.refresh(self.from_location.zone.usage, -self.quantity, pipe=pipe)
            self.procurement_detail.item.cache.refresh(self.to_location.zone.usage, self.quantity, pipe=pipe)
        pipe.execute()

    def confirm(self):
        with transaction.atomic():
            self.check_to_set_state('draft', set_state='confirmed', raise_exception=True)
            self.refresh_lock_item_quantity()
            return self

    def done(self, next_location=None):
        '''
        完成库存移动的动作,并自动根据需求状态和路线指定下一个库存移动
        1 需求尚未完成时,根据当前移动的路线区域获取下一个路线区域,若存在下一个路线区域且传入库位的区域与之相同,则完成移动并创建移动
        2 需求尚未完成时,根据当前移动的路线区域获取下一个路线区域,若存在下一个路线区域且传入库位的区域与之不同,则抛出错误
        3 需求尚未完成时,根据当前移动的路线区域获取下一个路线区域,若不存在下一个路线区域且传入了库位,则抛出错误
        4 需求尚未完成时,根据当前移动的路线区域获取下一个路线区域,若不存在下一个路线区域且未传入库位,
          则完成移动并检查需求下的所有移动是否均已完成,若完成则将需求置于完成状态
        :param next_location:Location instance
        :return: self
        '''
        with transaction.atomic():
            self.check_to_set_state('confirmed', set_state='done', raise_exception=True)
            procurement = self.procurement_detail.procurement
            route = self.procurement_detail.route
            cancel_state = procurement.check_states('cancel')
            if cancel_state and self.procurement_detail.direct_return:
                initial_setting = route.initial_setting
                next_zone_setting = None if (self.zone_setting == initial_setting) else initial_setting
            else:
                next_zone_setting = route.next_zone_setting(
                    now_zone_setting=self.zone_setting,
                    reverse=cancel_state
                )
            if next_zone_setting and not next_location:
                raise NotInStates('other', '存在下一个路线区域,但未传入相关的库位')
            if not next_zone_setting and next_location:
                raise NotInStates('other', '传入了相关的库位但不存在下一个路线区域')
            if next_location and next_zone_setting and next_location.zone != next_zone_setting.zone:
                raise NotInStates('other', '目标库位的区域与该移动的后续区域不同')
            self.refresh_item_quantity()
            if next_zone_setting:
                next_move = Move.objects.create(
                    from_location=self.to_location,
                    to_location=next_location,
                    zone_setting=next_zone_setting,
                    procurement_detail=self.procurement_detail,
                    quantity=self.quantity,
                    is_return=cancel_state,
                    state='draft'
                )
                self.to_move = next_move
                self.save()
            elif Move.check_state_queryset(
                    'done',
                    Move.objects.filter(procurement_detail__procurement=procurement)
            ) and not cancel_state:
                procurement.set_state('done')
            return self


# class PickOrder(StockOrder):
#     '''分拣表单'''
#     pass
#
# class CheckOrder(StockOrder):
#     '''送检表单'''
#     pass
#
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

class PackOrder(StockOrder):
    '''包裹表单'''

    pack_location = ActiveLimitForeignKey(
        'stock.Location',
        null=False,
        blank=False,
        verbose_name='包裹库位',
        related_name='pack_orders',
        help_text="进行打包或拆包动作的库位"
    )

    is_pack = models.BooleanField(
        '是否打包',
        default=True,
        help_text="是否进行打包操作的状态,True时打包,False时拆包"
    )

    package_nodes = models.ManyToManyField(
        'stock.PackageNode',
        through='stock.PackOrderLine',
        through_fields=('order','package_node'),
        verbose_name='包裹节点',
        related_name='pack_orders',
        help_text="包裹表单需要进行打包/拆包的包裹"
    )

    @property
    def state(self):
        return self.procurement.state

    def __str__(self):
        return 'pack-order-{}'.format(self.pack_location)

    class Meta:
        verbose_name = '包裹表单'
        verbose_name_plural = '包裹表单'

    @classmethod
    def create(cls, user, location):
        with transaction.atomic():
            procurement = Procurement.objects.create(user=user)
            return cls.objects.create(
                procurement=procurement,
                pack_location=location
            )

    def confirm(self):
        with transaction.atomic():
            self.procurement.check_states('draft', raise_exception=True)
            self.procurement.confirm()
            for line in self.lines.all():
                line.create_line_procurement_details()
            return self


class PackOrderLine(models.Model, StateMachine):
    '''打包表单的明细'''

    order = ActiveLimitForeignKey(
        'stock.PackOrder',
        null=False,
        blank=False,
        verbose_name='包裹表单',
        related_name='lines',
        help_text="明细归属的包裹表单"
    )

    package_node = models.ForeignKey(
        'stock.PackageNode',
        null=False,
        blank=False,
        verbose_name='包裹类型',
        related_name='pack_order_lines',
        limit_choices_to=PackageNode.States.root.query,
        help_text="需要进行打包的包裹类型"
    )

    quantity = models.PositiveSmallIntegerField(
        '数量',
        null=False,
        blank=False,
        help_text="包裹的所属数量"
    )

    procurement_details = models.ManyToManyField(
        'stock.ProcurementDetail',
        through='stock.PackOrderLineProcurementDetailSetting',
        through_fields=('line', 'detail'),
        verbose_name='需求明细',
        related_name='pack_order_lines',
        help_text="与打包明细相关的需求明细"
    )

    @property
    def package_detail(self):
        return self.procurement_details.get(item=self.package_node.item)

    @property
    def item_details(self):
        return self.procurement_details.exclude(item=self.package_node.item)

    def __str__(self):
        return '{}/{}'.format(self.order, self.package_node)

    class Meta:
        verbose_name = '包裹明细'
        verbose_name_plural = '包裹明细'
        unique_together = ('order', 'package_node')

    def _create_item_detail_settings(self):
        warehouse = self.order.pack_location.warehouse
        route = Route.get_default_route(warehouse, 'pack_closeout' if self.order.is_pack else 'closeout_pack')
        for setting in self.package_node.template.template_settings:
            detail = ProcurementDetail.objects.create(
                procurement=self.order.procurement,
                item=setting.type_setting.item,
                quantity=setting.quantiy * self.quantity,
                route=route
            )
            PackOrderLineProcurementDetailSetting.objects.create(
                line=self,
                node=self.package_node,
                template_setting=setting,
                procurement_detail=detail
            )
        for node in self.package_node.all_child_nodes:
            for setting in node.template.template_settings:
                detail = ProcurementDetail.objects.create(
                    procurement=self.order.procurement,
                    item=setting.type_setting.item,
                    quantity=setting.quantiy * self.quantity,
                    route=route
                )
                PackOrderLineProcurementDetailSetting.objects.create(
                    line=self,
                    node=node,
                    template_setting=setting,
                    procurement_detail=detail
                )

    def _create_package_detail_setting(self):
        warehouse = self.order.pack_location.zone.warehouse
        route = Route.get_default_route(warehouse, 'closeout_pack' if self.order.is_pack else 'pack_closeout')
        detail = ProcurementDetail.objects.create(
            procurement=self.order.procurement,
            item=self.package_node.item,
            quantity=self.quantity,
            route=route
        )
        PackOrderLineProcurementDetailSetting.objects.create(
            line=self,
            node=self.package_node,
            template_setting=None,
            procurement_detail=detail
        )

    def create_line_procurement_details(self):
        with transaction.atomic():
            self._create_item_detail_settings()
            self._create_package_detail_setting()

    def start(self):
        with transaction.atomic():
            pack_location = self.order.pack_location
            closeout_location = pack_location.zone.warehouse.closeout_location
            if not self.order.is_pack:
                pack_location, closeout_location = closeout_location, pack_location
            for detail in self.item_details:
                detail.start(pack_location, closeout_location)
            self.package_detail.start(closeout_location, pack_location)
            return self


class PackOrderLineProcurementDetailSetting(models.Model):
    '''打包表单的明细与需求明细关系表'''
    RELATED_NAME = 'pack_detail_settings'
    SIGNAL_RELATED_NAME = 'pack_detail_setting'

    line = models.ForeignKey(
        'stock.PackOrderLine',
        null=False,
        blank=False,
        verbose_name='包裹表单明细',
        related_name=RELATED_NAME,
        help_text="与需求明细相关的包裹表单明细"
    )

    detail = models.OneToOneField(
        'stock.ProcurementDetail',
        null=False,
        blank=False,
        verbose_name='需求明细',
        related_name=SIGNAL_RELATED_NAME,
        help_text="与打包表单明细相关的需求明细"
    )

    node = ActiveLimitForeignKey(
        'stock.PackageNode',
        null=False,
        blank=False,
        verbose_name='包裹节点',
        related_name=RELATED_NAME,
        help_text="生成该关系的包裹节点"
    )

    template_setting = models.ForeignKey(
        'stock.PackageTemplateItemSetting',
        null=True,
        blank=True,
        verbose_name='包裹模板设置',
        related_name=RELATED_NAME,
        help_text="生成该关系的包裹模板设置"
    )

    def __str__(self):
        return '{}/{}'.format(self.line, self.detail)

    class Meta:
        verbose_name = '包裹需求明细关系表'
        verbose_name_plural = '包裹需求明细关系表'


class ScrapOrder(StockOrder):
    '''报废单'''

    scrap_location = ActiveLimitForeignKey(
        'stock.Location',
        null=False,
        blank=False,
        verbose_name='退货地点',
        related_name='scrap_orders',
        help_text="发起报废需求的库位"
    )

    procurement_details = models.ManyToManyField(
        'stock.ProcurementDetail',
        through='stock.ScrapOrderLine',
        through_fields=('order','procurement_detail'),
        verbose_name='需求明细',
        related_name='scrap_orders',
        help_text="报废单的需求明细"
    )

    def __str__(self):
        return 'scrap-order-{}'.format(self.scrap_location)

    class Meta:
        verbose_name = '报废单'
        verbose_name_plural = '报废单'

    @classmethod
    def create(cls, user, location):
        with transaction.atomic():
            procurement = Procurement.objects.create(user=user)
            return cls.objects.create(procurement=procurement)

    def confirm(self):
        with transaction.atomic():
            self.procurement.check_states('draft',raise_exception=True)
            self.procurement.confirm()
            return self

    def create_detail(self,item,quantity):
        with transaction.atomic():
            zone = self.scrap_location.zone
            route = Route.get_default_route(zone.warehouse,'{}_scrap'.format(zone.usage))
            detail = ProcurementDetail.objects.create(
                procurement=self.procurement,
                item=item,
                quantity=quantity,
                route=route
            )
            ScrapOrderLine.objects.create(
                order=self,
                procurement_detail=detail
            )


class ScrapOrderLine(models.Model,StateMachine):
    '''报废单明细'''

    order = models.ForeignKey(
        'stock.ScrapOrder',
        null=False,
        blank=False,
        verbose_name='报废单',
        related_name='lines',
        help_text="报废单"
    )

    procurement_detail = models.OneToOneField(
        'stock.ProcurementDetail',
        null=False,
        blank=False,
        verbose_name='需求明细',
        related_name='scrap_order_lines',
        help_text="报废单的需求明细"
    )

    def __str__(self):
        return '{}/{}'.format(self.order,self.procurement_detail)

    class Meta:
        verbose_name = '报废单明细',
        verbose_name_plural = '报废单明细'

    def start(self):
        with transaction.atomic():
            from_location = self.order.scrap_location
            to_location = from_location.zone.warehouse.scrap_location
            self.procurement_detail.start(from_location,to_location)
            return self


class CloseoutOrder(StockOrder):
    '''平仓表单'''
    closeout_location = ActiveLimitForeignKey(
        'stock.Location',
        null=False,
        blank=False,
        verbose_name='平仓地点',
        related_name='closeout_orders',
        help_text="发起平仓需求的库位"
    )

    procurement_details = models.ManyToManyField(
        'stock.ProcurementDetail',
        through='stock.CloseoutOrderLine',
        through_fields=('order','procurement_detail'),
        verbose_name='需求明细',
        related_name='closeout_orders',
        help_text="平仓单的需求明细"
    )

    def __str__(self):
        return 'closeout-order-{}'.format(self.closeout_location)

    class Meta:
        verbose_name = '平仓表单'
        verbose_name_plural = '平仓表单'

    @classmethod
    def create(cls, user, location):
        with transaction.atomic():
            procurement = Procurement.objects.create(user=user)
            return cls.objects.create(procurement=procurement)

    def confirm(self):
        with transaction.atomic():
            self.procurement.check_states('draft', raise_exception=True)
            self.procurement.confirm()
            return self

    def create_detail(self, item, quantity):
        with transaction.atomic():
            zone = self.closeout_location.zone
            route = Route.get_default_route(zone.warehouse, '{}_scrap'.format(zone.usage))
            detail = ProcurementDetail.objects.create(
                procurement=self.procurement,
                item=item,
                quantity=quantity,
                route=route
            )
            CloseoutOrderLine.objects.create(
                order=self,
                procurement_detail=detail
            )


class CloseoutOrderLine(models.Model):
    '''平仓明细'''
    order = models.ForeignKey(
        'stock.CloseoutOrder',
        null=False,
        blank=False,
        verbose_name='平仓单',
        related_name='lines',
        help_text="平仓单"
    )

    procurement_detail = models.OneToOneField(
        'stock.ProcurementDetail',
        null=False,
        blank=False,
        verbose_name='需求明细',
        related_name='closeout_order_lines',
        help_text="平仓单的需求明细"
    )

    def __str__(self):
        return '{}/{}'.format(self.order,self.procurement_detail)

    class Meta:
        verbose_name = '平仓明细'
        verbose_name_plural = '平仓明细'

    def start(self):
        with transaction.atomic():
            from_location = self.order.closeout_location
            to_location = from_location.zone.warehouse.closeout_location
            self.procurement_detail.start(from_location,to_location)
            return self


class Route(BaseModel):
    '''路线'''
    ROUTE_TYPE = (
        ('produce-stock', '生产-库存路线'),
        ('produce-customer', '生产-销售路线'),
        ('produce-pack', '生产-包裹路线'),
        ('produce-produce', '生产调拨路线'),
        ('produce-closeout', '生产消耗路线'),

        ('stock-produce', '库存-生产路线'),
        ('stock-customer', '库存-销售路线'),
        ('stock-pack', '库存-包裹路线'),
        ('stock-stock', '库内调拨路线'),
        ('stock-closeout', '盘亏路线'),

        ('pack-stock', '包裹-库存路线'),
        ('pack-customer', '包裹-销售路线'),
        ('pack-produce', '包裹-生产路线'),
        ('pack-pack', '包裹调拨路线'),
        ('pack-closeout', '包裹消耗路线'),

        ('closeout-produce', '生产生成路线'),
        ('closeout-stock', '盘盈路线'),
        ('closeout-pack', '包裹生成路线'),

        ('supplier-stock', '采购-库存路线'),
        ('supplier-pack', '采购-打包路线'),
        ('supplier-customer', '采购-销售路线'),
        ('supplier-produce', '采购-生产路线'),

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

    route_type = models.CharField(
        '路线类型',
        null=False,
        blank=False,
        choices=ROUTE_TYPE,
        max_length=20,
        help_text="路线的业务类型"
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

    @property
    def length(self):
        return RouteZoneSetting.objects.filter(route=self).count()

    @property
    def initial_zone(self):
        return Zone.objects.get(warehouse=self.warehouse, usage=self.route_type.split('-')[0])

    @property
    def end_zone(self):
        return Zone.objects.get(warehouse=self.warehouse, usage=self.route_type.split('-')[1])

    @property
    def initial_setting(self):
        return RouteZoneSetting.objects.filter(route=self).first()

    @property
    def end_setting(self):
        return RouteZoneSetting.objects.filter(route=self).last()

    class Meta:
        verbose_name = '路线'
        verbose_name_plural = '路线'
        unique_together = ('warehouse', 'route_type', 'sequence')

    class States(BaseModel.States):
        active = BaseModel.States.active
        produce_stock = Statement(inherits=active, return_type='produce-stock')
        produce_customer = Statement(inherits=active, return_type='produce-customer')
        produce_pack = Statement(inherits=active, return_type='produce-pack')
        produce_produce = Statement(inherits=active, return_type='produce-produce')
        produce_closeout = Statement(inherits=active, return_type='produce-closeout')

        stock_produce = Statement(inherits=active, return_type='stock-produce')
        stock_customer = Statement(inherits=active, return_type='stock-customer')
        stock_pack = Statement(inherits=active, return_type='stock-pack')
        stock_stock = Statement(inherits=active, reutrn_type='stock-stock')
        stock_closeout = Statement(inherits=active, return_type='stock-closeout')

        pack_stock = Statement(inherits=active, return_type='pack-stock')
        pack_customer = Statement(inherits=active, return_type='pack-customer')
        pack_produce = Statement(inherits=active, return_type='pack-produce')
        pack_pack = Statement(inherits=active, return_type='pack-pack')
        pack_closeout = Statement(inherits=active, return_type='pack-closeout')

        closeout_produce = Statement(inherits=active, return_type='closeout-produce')
        closeout_stock = Statement(inherits=active, return_type='closeout-stock')
        closeout_pack = Statement(inherits=active, return_type='closeout-pack')

        supplier_stock = Statement(inherits=active, return_type='supplier-stock')
        supplier_pack = Statement(inherits=active, return_type='supplier-pack')
        supplier_customer = Statement(inherits=active, return_type='supplier-customer')
        supplier_produce = Statement(inherits=active, return_type='supplier-produce')

    @classmethod
    def get_default_route(cls, warehouse, route_type):
        return cls.get_state_instance(route_type, cls.objects.filter(warehouse=warehouse, sequence=0))

    def next_zone_setting(self, now_zone_setting, reverse=False):
        if not reverse:
            return RouteZoneSetting.objects.filter(
                route=self,
                sequence__gt=now_zone_setting.sequence
            ).first()
        else:
            return RouteZoneSetting.objects.filter(
                route=self,
                sequence__lt=now_zone_setting.sequence
            ).last()


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
        unique_together = ('route', 'sequence')
        ordering = ('sequence',)


class Procurement(BaseModel):
    '''需求'''

    user = PartnerForeignKey(
        null=False,
        blank=False,
        verbose_name='合作伙伴',
        help_text="提出需求的相关合作伙伴"
    )

    require_procurements = models.ManyToManyField(
        'self',
        verbose_name='前置需求',
        related_name='support_procurements',
        help_text="该需求的前置需求,只有当所有的前置需求都完成时,该需求的明细才能开始"
    )

    state = CancelableSimpleStateCharField(
        '状态',
        help_text="需求单的状态"
    )

    def __str__(self):
        return '{}-{}'.format(str(self.user), str(self.route))

    @property
    def doing_moves(self):
        return Move.get_state_queryset('doing', Move.objects.filter(procurement_detail__procurement=self))

    class Meta:
        verbose_name = '需求'
        verbose_name_plural = '需求'

    class States(BaseModel.States):
        active = BaseModel.States.active
        draft = Statement(inherits=active, state='draft')
        confirmed = Statement(inherits=active, state='confirmed')
        done = Statement(inherits=active, state='done')
        cancel = Statement(inherits=active, state='cancel')

    def confirm(self):
        self.check_to_set_state('draft', set_state='confirmed', raise_exception=True)
        return self

    def cancel(self):
        self.check_to_set_state('draft', 'confirmed', set_state='cancel', raise_exception=True)
        return self


class ProcurementDetail(models.Model, StateMachine):
    '''需求明细'''

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

    route = ActiveLimitForeignKey(
        'stock.Route',
        null=False,
        blank=False,
        verbose_name='路线',
        related_name='details',
        help_text="根据需求产生的位置以及指定的产品来源库位自动匹配的移动路线"
    )

    direct_return = models.BooleanField(
        '直接退货',
        default=False,
        help_text="回退方式,为True时直接返回,为False时按原路线返回"
    )

    def __str__(self):
        return '{}/{}'.format(str(self.procurement), str(self.item))

    class Meta:
        verbose_name = "需求明细"
        verbose_name_plural = "需求明细"

    class States:
        start_able = Statement(
            Q(moves__isnull=True) &
            (Q(procurement__require_procurements__isnull=True) | Q(procurement__require_procurements__state='done'))
        )
        started = Statement(Q(moves__isnull=False))

    @property
    def doing_move(self):
        return Move.get_state_queryset('doing').get(procurement_detail=self)

    def start(self, initial_location, next_location):
        with transaction.atomic():
            self.check_states('start_able', raise_exception=True)
            self.procurement.check_states('confirmed', raise_exception=True)
            Move.objects.create(
                from_location=initial_location,
                to_location=next_location,
                procurement_detail=self,
                zone_setting=RouteZoneSetting.objects.filter(route=self.route)[1],
                quantity=self.quantity,
                state='draft',
                is_return=False
            )
            return self


class Item(BaseModel):
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
            Q(content_type__app_label='product') & Q(content_type__model='Product'),
            inherits=active
        )
        package_node = Statement(
            Q(content_type__app_label='stock') & Q(content_type__model='PackageNode'),
            inherits=active
        )

    @property
    def cache(self):
        return CacheItem(self)
