#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from decimal import Decimal as D

from django.db import transaction
from django.db.models import Q, F, Value
from django.db.models.functions import Concat
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext as _
from django.contrib.contenttypes.models import ContentType
from django.core.validators import MinValueValidator

from common import Redis
from common.model import BaseModel, TreeModel
from common.exceptions import NotInStates
from common.fields import ActiveLimitForeignKey, ActiveLimitOneToOneField, CancelableSimpleStateCharField
from common.state import Statement, StateMachine
from common.validators import NotZeroValidator, StateInstanceValidator

from django_perm import models
from django_product.utils import QuantityField
from django_product.models import Item as SuperItem
from django_product.models import PackageNode as SuperPackageNode
from .utils import LocationForeignKey, INITIAL_ROUTE_SEQUENCE, END_ROUTE_SEQUENCE

User = get_user_model()

class Item(SuperItem):
    """
    proxy class that provide the cache
    """
    class Meta:
        proxy = True

    @property
    def cache(self):
        if not hasattr(self, '__cache'):
            self.__cache = CacheItem(self)
        return self.__cache

    @property
    def now_item_name(self):
        """
        get item key name
        :return: string
        """
        return CacheItem.item_name(self)

    @property
    def lock_item_name(self):
        """
        get item lock key name
        :return: string
        """
        return CacheItem.item_name(self, quantity_type='lock')

    @property
    def lock_item_name(self):
        """
        get item all key name
        :return: string
        """
        return CacheItem.item_name(self, quantity_type='all')


class CacheItem(object):
    """
    object reflect to stock item.
    as a manager which have all methods to control the quantity of item
    """
    ALL = {'stock', 'check', 'pack', 'wait', 'deliver'}
    SETTLED = {'customer'}
    TRANSPORTING = {'check', 'pack', 'wait', 'deliver'}
    SCRAP = {'scrap'}
    REPAIR = {'repair'}
    CLOSEOUT = {'closeout'}

    ALL_ITEM_NAME_TEMPLATE = 'all_item_{}'
    LOCK_ITEM_NAME_TEMPLATE = 'lock_item_{}'
    NOW_ITEM_NAME_TEMPLATE = 'now_item_{}'
    QUANTITY_TYPE = {'now', 'lock', 'all'}

    def __init__(self, item):
        """
        :param item: stock.Item instance
        """
        self.item = item

    @classmethod
    def item_name(cls, item, quantity_type='now'):
        """
        class method will return the key of item
        :param item: stock.Item instance
        :return: string
        """
        return getattr(cls, '{}_ITEM_NAME_TEMPLATE'.format(quantity_type.upper())).format(item.pk)

    def cache_name(self, quantity_type='now'):
        """
        the name for redis as the key,each warehouse has it own cache name
        :return: string
        """
        return self.item_name(self.item, quantity_type)

    def get_quantity(self, *zones, quantity_type='now'):
        """
        sum of item quantities figure out by set of v
        :param zones: set or string
        :return: decimal
        """

        redis = Redis()
        zones_set = set(zones)
        zone_list = set(Location.States.ZONE_STATES.keys())
        if not zones_set.difference(zone_list):
            return redis.zscore_sum(self.cache_name(quantity_type), *zones_set)
        raise NotInStates(_('zone'), _('unknown zone'))

    def all(self, quantity_type='now'):
        """
        sum of item in all zones
        :return: decimal
        """
        return self.get_quantity(*self.ALL, quantity_type=quantity_type)

    def settled(self, quantity_type='now'):
        """
        sum of item in settled zones
        :return: decimal
        """
        return self.get_quantity(*self.SETTLED, quantity_type=quantity_type)

    def transporting(self, quantity_type='now'):
        """
        sum of item in transporting zones
        :return: decimal
        """
        return self.get_quantity(*self.TRANSPORTING, quantity_type=quantity_type)

    def scrap(self, quantity_type='now'):
        """
        sum of item in scrap zones
        :return: decimal
        """
        return self.get_quantity(*self.SCRAP, quantity_type=quantity_type)

    def repair(self, quantity_type='now'):
        """
        sum of item in repair zones
        :return: decimal
        """
        return self.get_quantity(*self.REPAIR, quantity_type=quantity_type)

    def closeout(self, quantity_type='now'):
        """
        sum of item in closeout zones
        :return: decimal
        """
        return self.get_quantity(*self.CLOSEOUT, quantity_type=quantity_type)

    def _change(self, zone, quantity, quantity_type, pipe=None):
        """
        increase of decrease the quantity of item in the zone
        :param zone: string
        :param quantity: decimal
        :param pipe: pipeline of redis
        :return: 0 or 1
        """
        if zone in Location.States.ZONE_STATES.keys():
            if quantity_type in ('all', 'lock'):
                redis = pipe or Redis()
                result = redis.zincrby(self.cache_name(quantity_type=quantity_type), zone, quantity)
                if quantity_type == 'all':
                    redis.zincrby(self.cache_name('now'), zone, quantity)
                else:
                    redis.zincrby(self.cache_name('now'), zone, -quantity)
                return result
            raise AttributeError(quantity_type + _(' must be "all" or "lock".'))
        raise AttributeError(zone + _(' is unknown zone.'))

    def refresh(self, zone, quantity, pipe=None):
        return self._change(zone, quantity, quantity_type='all', pipe=pipe)

    def lock(self, zone, quantity, pipe=None):
        return self._change(zone, quantity, quantity_type='lock', pipe=pipe)

    def sync(self):
        """
        refresh all zones item quantity in the warehouse
        :return: self
        """
        redis = Redis()
        pipe = redis.pipeline()
        watch_keys = Warehouse.leaf_child_locations_cache_name
        pipe.watch(watch_keys)
        pipe.delete(self.cache_name('now'), self.cache_name('all'), self.cache_name('lock'))
        for warehouse in Warehouse.get_state_queryset('active'):
            for zone in Location.States.ZONE_STATES.keys():
                all_quantity = warehouse.get_item_quantity(
                    item=self.item,
                    zone=zone,
                    quantity_type='all',
                    pipe=pipe
                )
                pipe.zincrby(self.cache_name('all'), zone, all_quantity)
                lock_quantity = warehouse.get_item_quantity(
                    item=self.item,
                    zone=zone,
                    quantity_type='lock',
                    pipe=pipe
                )
                pipe.zincrby(self.cache_name('lock'), zone, lock_quantity)
        pipe.execute()
        return self

class CacheLocation(object):
    """
    object reflect to stock location.
    as a manager which have all methods to control the quantity of item in the location
    """
    LOCATION_NAME_TEMPLATE = 'location_{}'

    def __init__(self, location):
        """
        :param location: stock.Location instance
        """
        self.location = location

    @classmethod
    def location_name(cls, location):
        """
        the name of location in redis as key
        :param location: stock.Location
        :return: string
        """
        return cls.LOCATION_NAME_TEMPLATE.format(location.pk)

    @property
    def cache_name(self):
        """
        the name of location in redis as key
        :return: string
        """
        return self.location_name(self.location)

    def _change(self, item, quantity, quantity_type, pipe=None):
        """
        increase of decrease the quantity of item in the location
        :param item: stock.Item instance
        :param quantity: decimal
        :param quantity_type: string
        :param pipe: redis pipeline
        :return: 0 or 1
        """
        redis = pipe or Redis()
        return redis.zincrby(
            self.cache_name,
            CacheItem.item_name(item, quantity_type=quantity_type),
            quantity
        )

    def refresh(self, item, quantity, pipe=None):
        return self._change(item, quantity, quantity_type='all', pipe=pipe)

    def lock(self, item, quantity, pipe=None):
        return self._change(item, quantity, quantity_type='lock', pipe=pipe)

    def free_all(self, item, pipe=None):
        """
        delete the item score from location
        :param item: stock.Item instance
        :param pipe: redis pipeline
        :return: 0 or 1
        """
        redis = pipe or Redis()
        return redis.zrem(
            self.cache_name,
            CacheItem.item_name(item, quantity_type='lock')
        )

    def sync(self):
        """
        refresh all item quantity in the location
        :return: self
        """
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
        return self


class Warehouse(BaseModel):
    """
    warehouse have different zones
    """

    name = models.CharField(
        _('name'),
        null=False,
        blank=False,
        max_length=90,
        help_text=_('the name of warehouse')
    )

    manager = models.ForeignKey(
        User,
        null=False,
        blank=False,
        verbose_name=_('partner manage user'),
        help_text=_('partner user can manage this warehouse')
    )

    address = ActiveLimitForeignKey(
        'django_base.Address',
        null=False,
        blank=False,
        verbose_name=_('address'),
        help_text=_('the real address of warehouse')
    )

    root_location = ActiveLimitOneToOneField(
        'django_stock.Location',
        null=True,
        blank=True,
        verbose_name=_('root location'),
        related_name='root_warehouse',
        help_text=_('the root location of the warehouse')
    )

    def get_root_location(self, zone):
        """
        get root location of the zone
        :param zone: string
        :return: stock.Location instance
        """
        return Location.objects.get(
            warehouse=self,
            parent_node=self.root_location,
            zone=zone
        )

    @property
    def initial_location(self):
        """
        the default location of initial zone
        :return: stock.Location instance
        """
        return self.get_root_location('initial')

    @property
    def closeout_location(self):
        """
        the default location of closeout zone
        :return: stock.Location instance
        """
        return self.get_root_location('closeout')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('warehouse')
        verbose_name_plural = _('warehouses')

    def create_zones_and_routes(self):
        """
        create all zones of this warehouse,generally be called by create action in signal
        :return: self
        """
        with transaction.atomic():
            self.root_location = Location.objects.create(
                warehouse=self,
                zone='root',
                parent_node=None,
                is_virtual=True,
                index='',
                x='', y='', z=''
            )
            self.save()
            location_dict = {
                zone: Location.objects.create(
                    warehouse=self,
                    zone=zone,
                    parent_node=self.root_location,
                    index='-{}-'.format(self.root_location.pk),
                    is_virtual=zone not in Location.INDIVISIBLE_USAGE,
                    x='', y='', z=''
                ) for zone in Location.States.ZONE_STATES.keys() if zone != 'root'
            }
            for route_type, explain in Route.ROUTE_TYPE:
                route = Route.objects.create(
                    warehouse=self,
                    name='default/{}/{}'.format(self, route_type),
                    sequence=0
                )
                RouteSetting.objects.create(
                    name='initial',
                    route=route,
                    location=location_dict[route_type.split('_')[0]],
                    sequence=INITIAL_ROUTE_SEQUENCE
                )
                RouteSetting.objects.create(
                    name='end',
                    route=route,
                    location=location_dict[route_type.split('_')[1]],
                    sequence=END_ROUTE_SEQUENCE
                )
            return self

    @property
    def leaf_child_locations(self):
        """
        get all not virtual child locations of this warehouse
        :return: stock.Location queryset
        """
        return Location.get_state_queryset('no_virtual').filter(warehouse=self)

    @property
    def leaf_child_locations_cache_name(self):
        """
        get all not virtual child location's cache name
        :return: list
        """
        return [location.cache.cache_name for location in self.leaf_child_locations]

    def get_item_quantity(self, item, zone, quantity_type='now', pipe=None):
        """
        return the item quantity in zone
        :param item: stock.Item instance
        :param zone: string of zone or 'all'
        :return: decimal
        """
        if zone == 'root':
            return self.root_location.get_item_quantity(
                item=item,
                quantity_type=quantity_type,
                pipe=pipe
            )
        elif zone in Location.States.ZONE_STATES.keys():
            return self.get_root_location(zone).get_item_quantity(
                item=item,
                quantity_type=quantity_type,
                pipe=pipe
            )
        else:
            return D(0)


class Location(BaseModel, TreeModel):
    """
    the location in warehouse
    """
    ZONE = (
        ('stock', _('keep stock zone')),
        ('check', _('zone for checking')),
        ('pack', _('zone for packing')),
        ('wait', _('zone for waiting')),
        ('deliver', _('zone for deliver')),
        ('customer', _('zone for customer')),
        ('supplier', _('zone for supplier')),
        ('produce', _('zone for producing')),
        ('repair', _('zone for repairing')),
        ('scrap', _('zone for scrap')),
        ('closeout', _('zone for closeout')),
        ('initial', _('zone for initial')),
        ('root', _('zone for warehouse itself'))
    )
    INDIVISIBLE_USAGE = {'initial', 'closeout'}

    warehouse = ActiveLimitForeignKey(
        'django_stock.Warehouse',
        null=False,
        blank=False,
        verbose_name=_('warehouse'),
        help_text=_('the warehouse which contain the location')
    )

    zone = models.CharField(
        _('zone type'),
        null=False,
        blank=False,
        choices=ZONE,
        max_length=10,
        help_text=_('the zone type of location')
    )

    is_virtual = models.BooleanField(
        _('virtual status'),
        blank=True,
        default=False,
        help_text=_('when location is virtual,it can not contain stock item')
    )

    x = models.CharField(
        _('X coordinate'),
        null=False,
        blank=True,
        max_length=90,
        help_text=_('X coordinate in the same zone')
    )

    y = models.CharField(
        _('Y coordinate'),
        null=False,
        blank=True,
        max_length=90,
        help_text=_('Y coordinate in the same zone')
    )

    z = models.CharField(
        _('Z coordinate'),
        null=False,
        blank=True,
        max_length=90,
        help_text=_('Z coordinate in the same zone')
    )

    @property
    def location_name(self):
        """
        get the name of location key in redis
        :return: string
        """
        return CacheLocation.location_name(self)

    def __str__(self):
        return '{}/{}(X:{},Y:{},Z:{})'.format(self.warehouse, self.zone, self.x, self.y, self.z)

    class Meta:
        verbose_name = _('warehouse location')
        verbose_name_plural = _('warehouse locations')
        unique_together = (
            ('warehouse', 'zone', 'x', 'y', 'z'),
        )

    class States(BaseModel.States):
        active = Statement(
            (
                Q(warehouse__is_delete=False) &
                Q(warehouse__is_active=True)
            ),
            inherits=BaseModel.States.active
        )
        virtual = Statement(inherits=active, is_virtual=True)
        no_virtual = Statement(inherits=active, is_virtual=False)
        root = Statement(inherits=virtual, parent_node=None, zone='root')
        stock = Statement(inherits=active, zone='stock')
        check = Statement(inherits=active, zone='check')
        pack = Statement(inherits=active, zone='pack')
        wait = Statement(inherits=active, zone='wait')
        deliver = Statement(inherits=active, zone='deliver')
        customer = Statement(inherits=active, zone='customer')
        supplier = Statement(inherits=active, zone='supplier')
        produce = Statement(inherits=active, zone='produce')
        repair = Statement(inherits=active, zone='repair')
        scrap = Statement(inherits=active, zone='scrap')
        closeout = Statement(inherits=active, zone='closeout')
        initial = Statement(inherits=active, zone='initial')
        ZONE_STATES = {
            'root': root,
            'stock': stock,
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
        }

    def change_parent_node(self, node):
        """
        change this location's parent location
        the parent location must be virtual
        this location must be active
        :param node: stock.Location instance
        :return: self
        """
        if self.zone == node.zone and self.warehouse == node.warehouse:
            node.check_states('virtual', raise_exception=True)
            self.check_states('active', raise_exception=True)
            return super(Location, self).change_parent_node(node)
        raise NotInStates(_('other'), _("parent node's zone must equal to this location"))

    @property
    def leaf_child_locations(self):
        """
        get all no virtual location
        :return: stock.Location instance
        """
        return self.__class__.get_state_queryset('no_virtual', self.all_child_nodes)

    @property
    def leaf_child_location_cache_name(self):
        """
        get the list of all not virtual child location's cache name
        :return: list
        """
        return [location.location_name for location in self.leaf_child_locations]

    @property
    def cache(self):
        """
        :return: stock.CacheLocation instance
        """
        if not hasattr(self, '__cache'):
            self.__cache = CacheLocation(location=self)
        return self.__cache

    def in_sum(self, item):
        """
        get move in number of item to this location
        :param item: stock.Item instance
        :return: decimal
        """
        from django.db.models import Sum
        return Move.get_state_queryset('done').filter(
            to_location=self,
            procurement_detail__item=item
        ).aggregate(in_sum=Sum('quantity'))['in_sum'] or D(0)

    def out_sum(self, item):
        """
        get move out number of item from this location
        :param item: stock.Item instance
        :return: decimal
        """
        from django.db.models import Sum
        return Move.get_state_queryset('done').filter(
            from_location=self,
            procurement_detail__item=item
        ).aggregate(out_sum=Sum('quantity'))['out_sum'] or D(0)

    @classmethod
    def get_item_quantity_by_name(cls, name, item, quantity_type='now', pipe=None):
        """
        get the quantity of item in type by name
        :param name: string
        :param item: stock.Item instance
        :param quantity_type: string
        :return: decimal
        """
        redis = pipe or Redis()
        if quantity_type != 'now':
            result = redis.zscore(
                name,
                CacheItem.item_name(item, quantity_type)
            )
            return D(result) if result is not None else D(0)
        else:
            all_result = redis.zscore(
                name,
                CacheItem.item_name(item, 'all')
            )
            lock_result = redis.zscore(
                name,
                CacheItem.item_name(item, 'lock')
            )
            all_result = D(all_result) if all_result is not None else D(0)
            lock_result = D(lock_result) if lock_result is not None else D(0)
            return all_result - lock_result

    def get_item_quantity(self, item, quantity_type='now', pipe=None):
        """
        get the quantity of item in type
        :param item: stock.Item instance
        :param quantity_type: string
        :return: decimal
        """
        redis = pipe or Redis()
        if self.check_states('virtual'):
            redis.zunionstore(
                dest=self.location_name,
                keys=self.leaf_child_location_cache_name,
            )
        return self.get_item_quantity_by_name(
            name=self.location_name,
            item=item,
            quantity_type=quantity_type,
            pipe=redis
        )

class Move(BaseModel):
    """
    the move recording the start position and end position
    """

    from_location = LocationForeignKey(
        null=True,
        blank=True,
        verbose_name=_('from location'),
        related_name='out_moves',
        help_text=_('the start location move from')
    )

    to_location = LocationForeignKey(
        null=True,
        blank=True,
        verbose_name=_('to location'),
        related_name='in_moves',
        help_text=_('the end location move to')
    )

    to_move = ActiveLimitOneToOneField(
        'self',
        null=True,
        blank=True,
        verbose_name=_('to move'),
        related_name='from_moves',
        help_text=_('the next move when this move if complete')
    )

    procurement_detail = models.ForeignKey(
        'django_stock.ProcurementDetail',
        blank=False,
        verbose_name=_('procurement detail'),
        help_text=_('the procurement detail which create this move')
    )

    from_route_setting = models.ForeignKey(
        'django_stock.RouteSetting',
        null=False,
        blank=False,
        verbose_name=_('route zone setting'),
        related_name='from_moves',
        help_text=_('moves will be create according to the route,each move has it own zone setting')
    )

    to_route_setting = models.ForeignKey(
        'django_stock.RouteSetting',
        null=False,
        blank=False,
        verbose_name=_('route zone setting'),
        related_name='to_moves',
        help_text=_('moves will be create according to the route,each move has it own zone setting')
    )

    quantity = QuantityField(
        _('quantity'),
        null=False,
        blank=False,
        uom='item.instance.uom',
        validators=[MinValueValidator(0)],
        help_text=_('the number of item was moved')
    )

    state = CancelableSimpleStateCharField(
        _('status'),
        help_text=_('move status')
    )

    def __str__(self):
        return '{} -> {}'.format(
            self.from_location,
            self.to_location
        )

    class Meta:
        verbose_name = _('stock move')
        verbose_name_plural = _('stock moves')
        unique_together = ('procurement_detail', 'from_route_setting', 'to_route_setting')

    class States(BaseModel.States):
        active = BaseModel.States.active
        draft = Statement(inherits=active, state='draft')
        confirm_able = Statement(
            Q(from_location=F('from_route_setting__location')) |
            Q(from_location__index__startswith=Concat(
                F('from_route_setting__location__index'), F('from_route_setting__location__pk'), Value('-')
            ))
            ,
            inherits=draft
        )
        confirmed = Statement(inherits=active, state='confirmed')
        doing = Statement(Q(state='draft') | Q(state='confirmed'), inherits=active)
        done_able = Statement(
            Q(to_location=F('to_route_setting__location')) |
            Q(to_location__index__startswith=Concat(
                F('to_route_setting__location__index'), F('to_route_setting__location__pk'), Value('-')
            )),
            inherits=confirmed
        )
        done = Statement(inherits=active, state='done')
        cancel_able = Statement(Q(procurement_detail__procurement__state='cancel'), inherits=draft)
        cancel = Statement(inherits=active, state='cancel')

    def refresh_lock_item_quantity(self, pipe=None, reverse=False):
        """
        increase/decrease the lock number of item in the zone
        :pipe: redis pipeline
        :reverse: boolean
        :return: 0 or 1
        """
        return self.from_location.cache.lock(
            item=self.procurement_detail.item,
            quantity=self.quantity if not reverse else - self.quantity,
            pipe=pipe
        )

    def refresh_item_quantity(self):
        """
        increase/decrease the number of item in the zone
        :return: 0 or 1
        """
        redis = Redis().pipeline()
        self.from_location.cache.refresh(
            item=self.procurement_detail.item,
            quantity=(-self.quantity),
            pipe=redis
        )
        self.to_location.cache.refresh(
            item=self.procurement_detail.item,
            quantity=self.quantity,
            pipe=redis
        )
        self.refresh_lock_item_quantity(pipe=redis, reverse=True)
        if self.from_location.zone != self.to_location.zone:
            self.procurement_detail.item.cache.refresh(self.from_location.zone, -self.quantity, pipe=redis)
            self.procurement_detail.item.cache.refresh(self.to_location.zone, self.quantity, pipe=redis)
        redis.execute()

    def confirm(self, pipe=None):
        """
        change move status from draft to confirmed and increase the lock quantity of item in redis
        :pipe: redis pipeline
        :return: self
        """
        with transaction.atomic():
            self.check_to_set_state('confirm_able', set_state='confirmed', raise_exception=True)
            self.refresh_lock_item_quantity(pipe=pipe)
            return self

    def cancel(self, pipe=None):
        """
        change move status from cancel_able to cancel
        :pipe: redis pipeline
        :return:
        """
        with transaction.atomic():
            self.check_to_set_state('cancel_able', set_state='cancel', raise_exception=True)
            self.refresh_lock_item_quantity(reverse=True, pipe=pipe)
            self_cancel = self.check_states('cancel')
            procurement_cancel = self.procurement_detail.procurement.check_states('cancel')
            move = self.get_next_move(self_cancel,procurement_cancel)
            if move:
                move.save()
                self.to_move = move
                self.save()
                move.confirm()
            return self

    def get_next_move(self,self_cancel,procurement_cancel):
        """
        get the next move of this move
        :return: (stock.Move instance,boolean,boolean)
        """
        route = self.procurement_detail.route
        from_route_setting = self.from_route_setting if self_cancel else self.to_route_setting
        to_route_setting = route.next_route_setting(
            now_route_setting=from_route_setting,
            reverse=procurement_cancel
        )
        if to_route_setting:
            from_location = self.from_location if self_cancel else self.to_location
            to_location =to_route_setting.location if to_route_setting.location.check_states('no_virtual') else None
            return Move(
                from_location=from_location,
                to_location=to_location,
                from_route_setting=from_route_setting,
                to_route_setting=to_route_setting,
                procurement_detail=self.procurement_detail,
                quantity=self.quantity,
                state='draft'
            )
        return None

    def done(self):
        """
        完成库存移动的动作,并自动根据需求状态和路线指定下一个库存移动
        1 需求尚未完成时,根据当前移动的路线区域获取下一个路线区域,若存在下一个路线区域且传入库位的区域与之相同,则完成移动并创建移动
        2 需求尚未完成时,根据当前移动的路线区域获取下一个路线区域,若存在下一个路线区域且传入库位的区域与之不同,则抛出错误
        3 需求尚未完成时,根据当前移动的路线区域获取下一个路线区域,若不存在下一个路线区域且传入了库位,则抛出错误
        4 需求尚未完成时,根据当前移动的路线区域获取下一个路线区域,若不存在下一个路线区域且未传入库位,
          则完成移动并检查需求下的所有移动是否均已完成,若完成则将需求置于完成状态
        :pipe: redis pipeline
        :return: self
        """
        with transaction.atomic():
            self.check_to_set_state('done_able', set_state='done', raise_exception=True)
            procurement = self.procurement_detail.procurement
            self_cancel = self.check_states('cancel')
            procurement_cancel = procurement.check_states('cancel')
            move = self.get_next_move(self_cancel=self_cancel,procurement_cancel=procurement_cancel)
            self.refresh_item_quantity()
            if move:
                move.save()
                self.to_move = move
                self.save()
                move.confirm()
            elif Move.check_state_queryset(
                    'done',
                    Move.objects.filter(procurement_detail__procurement=procurement)
            ) and not procurement_cancel and not ProcurementDetail.objects.filter(
                move__isnull=True, procurement=procurement).exists():
                procurement.set_state('done')
            return self

class InitialOrder(BaseModel):
    """
    the order to create item in stock
    """
    procurement = ActiveLimitOneToOneField(
        'django_stock.Procurement',
        null=True,
        blank=True,
        verbose_name=_('procurement'),
        help_text=_('the procurement about this order')
    )

    location = ActiveLimitForeignKey(
        'django_stock.Location',
        null=False,
        blank=False,
        verbose_name=_('location'),
        validators=[StateInstanceValidator('stock')],
        help_text=_('the location to make operation')
    )

    create_user = models.ForeignKey(
        User,
        null=False,
        blank=False,
        verbose_name=_('create user'),
        help_text=_('the user who create this pack order')
    )

    procurement_details = models.ManyToManyField(
        'django_stock.ProcurementDetail',
        through='django_stock.InitialOrderLine',
        through_fields=('order', 'detail'),
        verbose_name=_('procurement details'),
        help_text=_('procurement details about initial operation')
    )

    @property
    def state(self):
        """
        the status of order,same as the procurement status
        :return: string
        """
        if self.procurement:
            return self.procurement.state
        return 'draft'

    def __str__(self):
        return 'initial-order-{}-{}'.format(self.location, self.pk)

    class Meta:
        verbose_name = _('initial order')
        verbose_name_plural = _('initial orders')

    class States(BaseModel.States):
        draft = Statement(Q(procurement__isnull=True), inherits=BaseModel.States.active)
        confirm_able = Statement(Q(packorderline__isnull=False), inherits=draft)
        confirmed = Statement(Q(procurement__state='confirmed'), inherits=BaseModel.States.active)
        done = Statement(Q(procurement__state='done'), inherits=BaseModel.States.active)

    def confirm(self):
        """
        change the status of procurement from draft to confirmed
        :return: self
        """
        with transaction.atomic():
            self.check_states('confirm_able', raise_exception=True)
            warehouse = self.location.warehouse
            initial_location = warehouse.get_root_location('initial')
            route = Route.get_default_route(warehouse=warehouse,route_type='initial_stock')
            self.procurement = Procurement.objects.create(
                warehouse=warehouse,
                user=self.create_user
            )
            self.save()
            lines = self.initialorderline_set.all()
            for line in lines:
                line.detail = ProcurementDetail.objects.create(
                    initial_location=initial_location,
                    end_location=self.location,
                    procurement=self.procurement,
                    item=line.item,
                    quantity=line.quantity,
                    route=route
                )
                line.save()
            self.procurement.confirm()
            for line in lines:
                line.detail.start().done()
            return self


class InitialOrderLine(models.Model, StateMachine):
    """
    order line of initial
    """
    order = ActiveLimitForeignKey(
        'django_stock.InitialOrder',
        null=False,
        blank=False,
        verbose_name=_('initial order'),
        help_text=_('v order')
    )

    detail = models.OneToOneField(
        'django_stock.ProcurementDetail',
        null=True,
        blank=True,
        verbose_name=_('procurement detail'),
        help_text=_('procurement detail of initial')
    )

    item = ActiveLimitForeignKey(
        'django_stock.Item',
        null=False,
        blank=False,
        verbose_name=_('item'),
        help_text=_('the item which will be initial')
    )

    quantity = QuantityField(
        _('quantity'),
        null=False,
        blank=False,
        uom='item.instance.uom',
        validators=[MinValueValidator(0)],
        help_text=_('the quantity of item')
    )

    def __str__(self):
        return '{}/{}'.format(self.order, self.detail)

    class Meta:
        verbose_name = _('initial order line')
        verbose_name_plural = _('initial order lines')
        unique_together = ('order', 'item')


class PackOrder(BaseModel):
    """
    the order to manage packing operation
    """

    procurement = ActiveLimitOneToOneField(
        'django_stock.Procurement',
        null=True,
        blank=True,
        verbose_name=_('procurement'),
        help_text=_('the procurement about this order')
    )

    location = ActiveLimitForeignKey(
        'django_stock.Location',
        null=False,
        blank=False,
        verbose_name=_('location'),
        validators=[StateInstanceValidator('pack')],
        help_text=_('the location to make operation')
    )

    create_user = models.ForeignKey(
        User,
        null=False,
        blank=False,
        verbose_name=_('create user'),
        help_text=_('the user who create this pack order')
    )

    is_pack = models.BooleanField(
        _('pack status'),
        default=True,
        help_text=_('True means the operation is packed,False means the operation is unpacking')
    )

    package_nodes = models.ManyToManyField(
        'django_product.PackageNode',
        through='django_stock.PackOrderLine',
        through_fields=('order', 'package_node'),
        verbose_name=_('package nodes'),
        help_text=_('all kinds of package node will be pack/unpack')
    )

    @property
    def state(self):
        """
        the status of order,same as the procurement status
        :return: string
        """
        if self.procurement:
            return self.procurement.state
        return 'draft'

    def __str__(self):
        return 'pack-order-{}-{}'.format(self.location, self.pk)

    class Meta:
        verbose_name = _('pack order')
        verbose_name_plural = _('pack orders')

    class States(BaseModel.States):
        draft = Statement(Q(procurement__isnull=True), inherits=BaseModel.States.active)
        confirm_able = Statement(Q(packorderline__isnull=False), inherits=draft)
        confirmed = Statement(Q(procurement__state='confirmed'), inherits=BaseModel.States.active)
        done = Statement(Q(procurement__state='done'), inherits=BaseModel.States.active)

    def confirm(self):
        """
        change the status of procurement from draft to confirmed
        :return: self
        """
        with transaction.atomic():
            self.check_states('confirm_able', raise_exception=True)
            self.procurement = Procurement.objects.create(
                warehouse=self.location.warehouse,
                user=self.create_user
            )
            self.save()
            for line in self.packorderline_set.all():
                line.create_procurement_detail()
            self.procurement.confirm()
            return self


class PackOrderLine(models.Model, StateMachine):
    """
    the pack order line bind to procurement details
    """

    order = ActiveLimitForeignKey(
        'django_stock.PackOrder',
        null=False,
        blank=False,
        verbose_name=_('pack order'),
        help_text=_('pack order')
    )

    package_node = models.ForeignKey(
        'django_product.PackageNode',
        null=False,
        blank=False,
        verbose_name=_('package node'),
        help_text=_('package node the procurement will be pack/unpack')
    )

    quantity = models.PositiveSmallIntegerField(
        _('quantity'),
        null=False,
        blank=False,
        validators=[MinValueValidator(0)],
        help_text=_('the number of package will be pack/unpack')
    )

    procurement_details = models.ManyToManyField(
        'django_stock.ProcurementDetail',
        through='django_stock.PackOrderLineSetting',
        through_fields=('line', 'detail'),
        verbose_name=_('procurement details'),
        help_text=_('the procurement details about the package node')
    )

    @property
    def package_detail(self):
        """
        the procurement detail about package node
        :return: stock.ProcurementDetail instance
        """
        return self.procurement_details.filter(item=self.package_node.item).first()

    @property
    def item_details(self):
        """
        the procurement details about stock item
        :return: stock.ProcurementDetail queryset
        """
        return self.procurement_details.exclude(item=self.package_node.item)

    def __str__(self):
        return '{}/{}'.format(self.order, self.package_node)

    class Meta:
        verbose_name = _('pack order line')
        verbose_name_plural = _('pack order lines')
        unique_together = ('order', 'package_node')

    def create_procurement_detail(self):
        with transaction.atomic():
            from functools import reduce
            warehouse = self.order.location.warehouse
            forward_route = Route.get_default_route(warehouse, 'pack_closeout')
            backward_route = Route.get_default_route(warehouse, 'closeout_pack')
            initial_location = self.order.location
            end_location = warehouse.closeout_location
            if not self.order.is_pack:
                forward_route, backward_route = backward_route, forward_route
                initial_location, end_location = end_location, initial_location
            for setting in self.package_node.template.packagetemplatesetting_set.all():
                detail = ProcurementDetail.objects.create(
                    initial_location=initial_location,
                    end_location=end_location,
                    procurement=self.order.procurement,
                    item=setting.type_setting.item,
                    quantity=setting.quantity * self.quantity,
                    route=forward_route
                )
                PackOrderLineSetting.objects.create(
                    line=self,
                    node=self.package_node,
                    template_setting=setting,
                    detail=detail
                )
            quantity_dict = self.package_node.child_quantity_dict
            quantity_dict[self.package_node.pk] = self.quantity
            for node in self.package_node.all_child_nodes:
                quantity = reduce(lambda a, b: a * b, map(
                    lambda index: quantity_dict[int(index)],
                    node.index.split('-')[:-1]
                ))
                for setting in node.template.packagetemplatesetting_set.all():
                    detail = ProcurementDetail.objects.create(
                        initial_location=initial_location,
                        end_location=end_location,
                        procurement=self.order.procurement,
                        item=setting.type_setting.item,
                        quantity=setting.quantiy * quantity,
                        route=forward_route
                    )
                    PackOrderLineSetting.objects.create(
                        line=self,
                        detail=detail,
                        node=node,
                        template_setting=setting
                    )
            detail = ProcurementDetail.objects.create(
                initial_location=end_location,
                end_location=initial_location,
                procurement=self.order.procurement,
                item=self.package_node.item,
                quantity=self.quantity,
                route=backward_route
            )
            PackOrderLineSetting.objects.create(
                line=self,
                detail=detail,
                node=self.package_node,
                template_setting=None
            )
            return self

    def done(self):
        """
        complete the item procurement detail and package node procurement detail
        :return: self
        """
        with transaction.atomic():
            for detail in self.procurement_details.all():
                detail.start().done()
            return self


class PackOrderLineSetting(models.Model):
    """
    config the one to many relationship with pack order line and procurement detail
    """

    line = models.ForeignKey(
        'django_stock.PackOrderLine',
        null=False,
        blank=False,
        verbose_name=_('pack order line'),
        help_text=_('the pack order line which procurement detail bind with')
    )

    detail = models.OneToOneField(
        'django_stock.ProcurementDetail',
        null=False,
        blank=False,
        verbose_name=_('procurement detail'),
        help_text=_('procurement detail bind with pack order line which config the package node')
    )

    node = ActiveLimitForeignKey(
        'django_product.PackageNode',
        null=False,
        blank=False,
        verbose_name=_('package node'),
        help_text=_('package node which procurement detail was created by')
    )

    template_setting = models.ForeignKey(
        'django_product.PackageTemplateSetting',
        null=True,
        blank=True,
        verbose_name=_('package template setting'),
        help_text=_('package template setting about packing item')
    )

    def __str__(self):
        return '{}/{}'.format(self.line, self.detail)

    class Meta:
        verbose_name = _('pack order line - procurement detail relationship')
        verbose_name_plural = _('pack order line - procurement detail relationships')


class CloseoutOrder(BaseModel):
    """
    the order to manage closeout operation
    """

    procurement = ActiveLimitOneToOneField(
        'django_stock.Procurement',
        null=True,
        blank=True,
        verbose_name=_('procurement'),
        help_text=_('the procurement about this order')
    )

    location = ActiveLimitForeignKey(
        'django_stock.Location',
        null=False,
        blank=False,
        verbose_name=_('location'),
        validators=[StateInstanceValidator('stock')],
        help_text=_('the location to make operation')
    )

    create_user = models.ForeignKey(
        User,
        null=False,
        blank=False,
        verbose_name=_('create user'),
        help_text=_('the user who create this pack order')
    )

    procurement_details = models.ManyToManyField(
        'django_stock.ProcurementDetail',
        through='django_stock.CloseoutOrderLine',
        through_fields=('order', 'detail'),
        verbose_name=_('procurement details'),
        help_text=_('procurement details about closeout operation')
    )

    @property
    def state(self):
        """
        the status of order,same as the procurement status
        :return: string
        """
        if self.procurement:
            return self.procurement.state
        return 'draft'

    def __str__(self):
        return 'closeout-order-{}'.format(self.location, self.pk)

    class Meta:
        verbose_name = _('closeout order')
        verbose_name_plural = _('closeout orders')

    class States(BaseModel.States):
        draft = Statement(Q(procurement__isnull=True), inherits=BaseModel.States.active)
        confirm_able = Statement(Q(closeoutorderline__isnull=False), inherits=draft)
        confirmed = Statement(Q(procurement__state='confirmed'), inherits=BaseModel.States.active)
        done = Statement(Q(procurement__state='done'), inherits=BaseModel.States.active)

    def confirm(self):
        """
        change the status of procurement from draft to confirmed
        :return: self
        """
        with transaction.atomic():
            self.check_states('confirm_able', raise_exception=True)
            self.procurement = Procurement.objects.create(
                warehouse=self.location.warehouse,
                user=self.create_user
            )
            self.save()
            lines = self.closeoutorderline_set.all()
            warehouse = self.location.warehouse
            closeout_location = warehouse.closeout_location
            closeout_stock_route = Route.get_default_route(warehouse, 'closeout_stock')
            stock_closeout_route = Route.get_default_route(warehouse, 'stock_closeout')
            for line in lines:
                from_location, to_location = (
                    (self.location, closeout_location)
                    if line.quantity > 0 else
                    (closeout_location, self.location)
                )
                route = stock_closeout_route if line.quantity > 0 else closeout_stock_route
                line.detail = ProcurementDetail.objects.create(
                    initial_location=from_location,
                    end_location=to_location,
                    procurement=self.procurement,
                    item=line.item,
                    quantity=abs(line.quantity),
                    route=route
                )
                line.save()
            self.procurement.confirm()
            for line in lines:
                line.detail.start().done()
            return self


class CloseoutOrderLine(models.Model, StateMachine):
    """
    order line of closeout
    """
    order = ActiveLimitForeignKey(
        'django_stock.CloseoutOrder',
        null=False,
        blank=False,
        verbose_name=_('closeout order'),
        help_text=_('closeout order')
    )

    detail = models.OneToOneField(
        'django_stock.ProcurementDetail',
        null=True,
        blank=True,
        verbose_name=_('procurement detail'),
        help_text=_('procurement detail of closeout')
    )

    item = ActiveLimitForeignKey(
        'django_stock.Item',
        null=False,
        blank=False,
        verbose_name=_('item'),
        help_text=_('the item which will be closeout')
    )

    quantity = QuantityField(
        _('quantity'),
        null=False,
        blank=False,
        uom='item.instance.uom',
        validators=[NotZeroValidator],
        help_text=_('the quantity of item')
    )

    def __str__(self):
        return '{}/{}'.format(self.order, self.detail)

    class Meta:
        verbose_name = _('closeout order line')
        verbose_name_plural = _('closeout order lines')
        unique_together = ('order', 'item')

class ScrapOrder(BaseModel):
    """
    the order to manage scrap operation
    """

    procurement = ActiveLimitOneToOneField(
        'django_stock.Procurement',
        null=True,
        blank=True,
        verbose_name=_('procurement'),
        help_text=_('the procurement about this order')
    )

    location = ActiveLimitForeignKey(
        'django_stock.Location',
        null=False,
        blank=False,
        verbose_name=_('location'),
        validators=[StateInstanceValidator(
            'pack', 'produce', 'stock', 'repair', 'check'
        )],
        help_text=_('the location to make operation')
    )

    create_user = models.ForeignKey(
        User,
        null=False,
        blank=False,
        verbose_name=_('create user'),
        help_text=_('the user who create this order')
    )

    route = ActiveLimitForeignKey(
        'django_stock.Route',
        null=True,
        blank=False,
        verbose_name=_('scrap route'),
        validators=[StateInstanceValidator(
            'produce_scrap', 'stock_scrap', 'pack_scrap',
            'repair_scrap', 'check_scrap'
        )],
        help_text=_('the route for order')
    )

    procurement_details = models.ManyToManyField(
        'django_stock.ProcurementDetail',
        through='django_stock.ScrapOrderLine',
        through_fields=('order', 'detail'),
        verbose_name=_('procurement details'),
        help_text=_('scrap procurement details makes by this order')
    )

    @property
    def state(self):
        """
        the status of order,same as the procurement status
        :return: string
        """
        if self.procurement:
            return self.procurement.state
        return 'draft'

    def __str__(self):
        return 'scrap-order-{}-{}'.format(self.location, self.pk)

    class Meta:
        verbose_name = _('scrap order')
        verbose_name_plural = _('scrap orders')

    class States(BaseModel.States):
        draft = Statement(Q(procurement__isnull=True), inherits=BaseModel.States.active)
        confirm_able = Statement(Q(scraporderline__isnull=False), inherits=draft)
        confirmed = Statement(Q(procurement__state='confirmed'), inherits=BaseModel.States.active)
        done = Statement(Q(procurement__state='done'), inherits=BaseModel.States.active)

    def confirm(self):
        """
        change the status of procurement from draft to confirmed
        :return: self
        """
        with transaction.atomic():
            self.check_states('confirm_able', raise_exception=True)
            self.procurement = Procurement.objects.create(
                warehouse=self.location.warehouse,
                user=self.create_user
            )
            self.save()
            lines = self.scraporderline_set.all()
            for line in lines:
                line.detail = ProcurementDetail.objects.create(
                    initial_location=self.location,
                    procurement=self.procurement,
                    item=line.item,
                    quantity=line.quantity,
                    route=self.route
                )
                line.save()
            self.procurement.confirm()
            for line in lines:
                line.detail.start()
            return self


class ScrapOrderLine(models.Model, StateMachine):
    """
    the scrap order line bind to procurement detail
    """

    order = ActiveLimitForeignKey(
        'django_stock.ScrapOrder',
        null=False,
        blank=False,
        verbose_name=_('scrap order'),
        help_text=_('scrap order')
    )

    item = ActiveLimitForeignKey(
        'django_stock.Item',
        null=False,
        blank=False,
        verbose_name=_('item'),
        help_text=_('the item which will be scraped')
    )

    quantity = QuantityField(
        _('quantity'),
        null=False,
        blank=False,
        uom='item.instance.uom',
        validators=[MinValueValidator(0)],
        help_text=_('the quantity of item')
    )

    detail = models.OneToOneField(
        'django_stock.ProcurementDetail',
        null=True,
        blank=True,
        verbose_name=_('procurement detail'),
        help_text=_('the procurement detail which order line bind with')
    )

    def __str__(self):
        return '{}/{}'.format(self.order, self.detail)

    class Meta:
        verbose_name = _('scrap order line')
        verbose_name_plural = _('scrap order lines')
        unique_together = ('order', 'item')

class RepairOrder(BaseModel):
    """
    the order of make repair operation of item
    """

    procurement = ActiveLimitOneToOneField(
        'django_stock.Procurement',
        null=True,
        blank=True,
        verbose_name=_('procurement'),
        help_text=_('the procurement about this order')
    )

    location = ActiveLimitForeignKey(
        'django_stock.Location',
        null=False,
        blank=False,
        verbose_name=_('location'),
        validators=[StateInstanceValidator(
            'produce', 'stock', 'pack', 'check', 'customer'
        )],
        help_text=_('the location to make operation')
    )

    route = ActiveLimitForeignKey(
        'django_stock.Route',
        null=False,
        blank=False,
        verbose_name=_('route'),
        validators=[StateInstanceValidator(
            'produce_repair', 'repair_produce',
            'pack_repair', 'repair_pack',
            'customer_repair', 'repair_customer',
            'stock_repair', 'repair_stock',
            'check_repair', 'repair_check'
        )],
    )

    create_user = models.ForeignKey(
        User,
        null=False,
        blank=False,
        verbose_name=_('create user'),
        help_text=_('the user who create this pack order')
    )

    procurement_details = models.ManyToManyField(
        'django_stock.ProcurementDetail',
        through='django_stock.RepairOrderLine',
        through_fields=('order', 'detail'),
        verbose_name=_('procurement details'),
        help_text=_('procurement details about repair operation')
    )

    @property
    def state(self):
        """
        the status of order,same as the procurement status
        :return: string
        """
        if self.procurement:
            return self.procurement.state
        return 'draft'

    def __str__(self):
        return 'repair-order-{}'.format(self.location, self.pk)

    class Meta:
        verbose_name = _('repair order')
        verbose_name_plural = _('repair orders')

    class States(BaseModel.States):
        draft = Statement(Q(procurement__isnull=True), inherits=BaseModel.States.active)
        confirm_able = Statement(
            (Q(location__zone='produce') & Q(route__route_type__in=('produce_repair', 'repair_produce'))) |
            (Q(location__zone='stock') & Q(route__route_type__in=('stock_repair', 'repair_stock'))) |
            (Q(location__zone='pack') & Q(route__route_type__in=('pack_repair', 'repair_pack'))) |
            (Q(location__zone='check') & Q(route__route_type__in=('check_repair', 'repair_check'))) |
            (Q(location__zone='customer') & Q(route__route_type__in=('customer_repair', 'repair_customer'))),
            inherits=draft
        )
        confirmed = Statement(Q(procurement__state='confirmed'), inherits=BaseModel.States.active)
        done = Statement(Q(procurement__state='done'), inherits=BaseModel.States.active)

    def confirm(self):
        """
        change the status of procurement from draft to confirmed
        :return: self
        """
        with transaction.atomic():
            self.check_states('confirm_able', raise_exception=True)
            self.procurement = Procurement.objects.create(
                warehouse=self.location.warehouse,
                user=self.create_user)
            self.save()
            for line in self.repairorderline_set.all():
                line.detail = ProcurementDetail.objects.create(
                    initial_locatin=self.location,
                    procurement=self.procurement,
                    item=line.item,
                    quantity=abs(line.quantity),
                    route=self.route,
                )
                line.save()
            self.procurement.confirm()
            return self


class RepairOrderLine(models.Model, StateMachine):
    """
    order line of repair
    """
    order = ActiveLimitForeignKey(
        'django_stock.RepairOrder',
        null=False,
        blank=False,
        verbose_name=_('repair order'),
        help_text=_('repair order')
    )

    detail = models.OneToOneField(
        'django_stock.ProcurementDetail',
        null=True,
        blank=True,
        verbose_name=_('procurement detail'),
        help_text=_('procurement detail of repair')
    )

    item = ActiveLimitForeignKey(
        'django_stock.Item',
        null=False,
        blank=False,
        verbose_name=_('item'),
        help_text=_('the item which will be repair')
    )

    quantity = QuantityField(
        _('quantity'),
        null=False,
        blank=False,
        uom='item.instance.uom',
        validators=[NotZeroValidator],
        help_text=_('the quantity of item')
    )

    def __str__(self):
        return '{}/{}'.format(self.order, self.detail)

    class Meta:
        verbose_name = _('repair order line')
        verbose_name_plural = _('repair order lines')
        unique_together = ('order', 'item')


class PickOrder(BaseModel):
    """"""

    procurement = ActiveLimitOneToOneField(
        'django_stock.Procurement',
        null=True,
        blank=True,
        verbose_name=_('procurement'),
        help_text=_('the procurement about this order')
    )

    location = ActiveLimitForeignKey(
        'django_stock.Location',
        null=False,
        blank=False,
        verbose_name=_('location'),
        validators=[StateInstanceValidator(
            'produce', 'stock', 'pack', 'repair',
            'check', 'customer', 'supplier'
        )],
        help_text=_('the location to make operation')
    )

    create_user = models.ForeignKey(
        User,
        null=False,
        blank=False,
        verbose_name=_('create user'),
        help_text=_('the user who create this order')
    )

    route = ActiveLimitForeignKey(
        'django_stock.Route',
        null=True,
        blank=False,
        verbose_name=_('scrap route'),
        validators=[StateInstanceValidator(
            'produce_stock', 'stock_stock', 'pack_stock',
            'produce_customer', 'stock_customer', 'pack_customer',
            'produce_pack', 'stock_pack', 'pack_pack',
            'produce_produce', 'stock_produce', 'pack_produce',
            'produce_repair', 'stock_repair', 'pack_repair',
            'supplier_stock', 'supplier_stock', 'supplier_produce',
            'repair_scrap', 'repair_customer', 'repair_check',
            'repair_produce', 'repair_stock', 'repair_pack',
            'scrap_repair', 'customer_repair', 'check_repair'
        )],
        help_text=_('the route for order to scrap')
    )

    procurement_details = models.ManyToManyField(
        'django_stock.ProcurementDetail',
        through='django_stock.PickOrderLine',
        through_fields=('order', 'detail'),
        verbose_name=_('procurement details'),
        help_text=_('scrap procurement details makes by this order')
    )

    def confirm(self):
        """
        change the status of procurement from draft to confirmed
        :return: self
        """
        with transaction.atomic():
            self.procurement.confirm()
            return self

    class Meta:
        verbose_name = _('inner order')
        verbose_name_plural = _('inner orders')

    def __str__(self):
        return 'inner-order-{}'.format(self.pk)


class PickOrderLine(models.Model, StateMachine):
    """
    inner order line for make moving according inner route
    """
    order = ActiveLimitForeignKey(
        'django_stock.PickOrder',
        null=False,
        blank=False,
        verbose_name=_('inner order'),
        help_text=_('inner order which this order line belongs to')
    )

    detail = models.OneToOneField(
        'django_stock.ProcurementDetail',
        null=False,
        blank=False,
        verbose_name=_('procurement detail'),
        help_text=_('the procurement detail which order line bind with')
    )

    def __str__(self):
        return '{}/{}'.format(self.order, self.detail)

    class Meta:
        verbose_name = _('inner order line')
        verbose_name_plural = _('inner order lines')

    def start(self):
        """
        start moving the inner procurement detail item
        :return: self
        """
        with transaction.atomic():
            from_location = self.order.scrap_location
            to_location = from_location.warehouse.scrap_location
            self.detail.start(from_location, to_location)
            return self


class Route(BaseModel):
    """
    the route of zone to chain together
    """
    ROUTE_TYPE = (
        # initial
        ('initial_stock', _('initial to stock route')),
        # pack
        ('pack_closeout', _('pack to closeout route')),
        ('closeout_pack', _('closeout to pack route')),
        # closeout
        ('stock_closeout', _('stock to closeout route')),
        ('closeout_stock', _('closeout to stock route')),
        # produce
        ('produce_closeout', _('produce to closeout route')),
        ('closeout_produce', _('closeout to produce route')),
        # scrap
        ('produce_scrap', _('produce to scrap route')),
        ('stock_scrap', _('stock to scrap route')),
        ('pack_scrap', _('pack to scrap route')),
        ('repair_scrap', _('repair to scrap route')),
        ('check_scrap', _('check to scrap route')),
        # inner
        ('stock_stock', _('stock to stock route')),
        ('produce_produce', _('produce to produce route')),
        ('pack_pack', _('pack to pack route')),
        ('scrap_scrap', _('scrap to scrap route')),
        ('repair_repair', _('repair to repair route')),
        ('check_check', _('check to check route')),
        # pick
        ('produce_stock', _('produce to stock route')),
        ('produce_pack', _('produce to pack route')),
        ('stock_pack', _('stock to pack route')),
        ('stock_produce', _('stock to produce route')),
        ('pack_stock', _('pack to stock route')),
        ('pack_produce', _('pack to produce route')),
        ('stock_check', _('stock to check route')),
        # customer
        ('produce_customer', _('produce to customer route')),
        ('stock_customer', _('stock to customer route')),
        ('pack_customer', _('pack to customer route')),
        # supplier
        ('supplier_stock', _('supplier to stock route')),
        ('supplier_pack', _('supplier to pack route')),
        ('supplier_produce', _('supplier to produce route')),
        # repair
        ('repair_stock', _('repair to stock route')),
        ('repair_customer', _('repair to customer route')),
        ('repair_pack', _('repair to pack route')),
        ('repair_produce', _('repair to produce route')),
        ('repair_check', _('repair to check route')),
        ('stock_repair', _('stock to repair route')),
        ('customer_repair', _('customer to repair route')),
        ('pack_repair', _('pack to repair route')),
        ('produce_repair', _('produce to repair route')),
        ('check_repair', _('check to repair route')),
    )

    INITIAL_ROUTES = {'initial_stock'}
    PACK_ROUTES = {'pack_closeout','closeout_pack'}
    CLOSEOUT_ROUTES = {'stock_closeout','closeout_stock'}
    PRODUCE_ROUTES = {'produce_closeout','closeout_produce'}
    SCRAP_ROUTES = {
        'produce_scrap',
        'stock_scrap',
        'pack_scrap',
        'repair_scrap',
        'check_scrap',
    }
    INNER_ROUTES = {
        'stock_stock','produce_produce','pack_pack',
        'scrap_scrap','check_check','repair_repair'
    }
    PICK_ROUTES = {
        'produce_stock', 'stock_produce',
        'produce_pack', 'pack_produce',
        'stock_pack', 'pack_stock',
        'stock_check'
    }
    REPAIR_ROUTES = {
        'produce_repair',
        'stock_repair',
        'pack_repair',
        'customer_repair',
        'check_repair',

        'repair_stock',
        'repair_customer',
        'repair_pack',
        'repair_produce',
        'repair_check',
    }
    CUSTOMER_ROUTES = {
        'stock_customer',
        'produce_customer',
        'pack_customer',
    }
    SUPPLIER_ROUTES = {
        'supplier_stock',
        'supplier_pack',
        'supplier_produce',
    }

    name = models.CharField(
        _('name'),
        null=False,
        blank=False,
        unique=True,
        max_length=190,
        help_text=_('the name of route')
    )

    warehouse = ActiveLimitForeignKey(
        'django_stock.Warehouse',
        null=False,
        blank=False,
        verbose_name=_('warehouse'),
        help_text=_('the warehouse which route belongs to')
    )

    route_type = models.CharField(
        _('route type'),
        null=True,
        blank=False,
        default=None,
        max_length=20,
        help_text=_('the type of route')
    )

    locations = models.ManyToManyField(
        'django_stock.Location',
        through='django_stock.RouteSetting',
        through_fields=('route', 'location'),
        blank=False,
        verbose_name=_('locations'),
        related_name='route_set',
        help_text=_('the location chain to be route')
    )

    initial_setting = ActiveLimitOneToOneField(
        'django_stock.RouteSetting',
        null=True,
        blank=True,
        verbose_name=_('initial setting'),
        related_name='initial_route',
        help_text=_('the initial setting of the route')
    )

    end_setting = ActiveLimitOneToOneField(
        'django_stock.RouteSetting',
        null=True,
        blank=True,
        verbose_name=_('end setting'),
        related_name='end_route',
        help_text=_('the end setting of the route')
    )

    users = models.ManyToManyField(
        User,
        blank=False,
        verbose_name=_('users'),
        help_text=_('the users who can use this route')
    )

    sequence = models.PositiveSmallIntegerField(
        _('sequence'),
        null=False,
        blank=False,
        default=0,
        help_text=_('the sequence of route,more smaller more important')
    )

    def __str__(self):
        return self.name

    @property
    def length(self):
        """
        the count of route's zones
        :return: int
        """
        return RouteSetting.objects.filter(route=self).count()

    class Meta:
        verbose_name = _('route')
        verbose_name_plural = _('routes')

    class States(BaseModel.States):

        active = BaseModel.States.active
        initial_stock= Statement(inherits=active, route_type='initial_stock')

        stock_closeout = Statement(inherits=active, route_type='stock_closeout')
        closeout_stock = Statement(inherits=active, route_type='closeout_stock')

        produce_closeout = Statement(inherits=active, route_type='produce_closeout')
        closeout_produce = Statement(inherits=active, route_type='closeout_produce')

        pack_closeout = Statement(inherits=active, route_type='pack_closeout')
        closeout_pack = Statement(inherits=active, route_type='closeout_pack')

        produce_scrap = Statement(inherits=active, route_type='produce_scrap')
        stock_scrap = Statement(inherits=active, route_type='stock_scrap')
        pack_scrap = Statement(inherits=active, route_type='pack_scrap')
        repair_scrap = Statement(inherits=active, route_type='repair_scrap')
        check_scrap = Statement(inherits=active, route_type='check_scrap')

        stock_stock = Statement(inherits=active, route_type='stock_stock')
        produce_produce = Statement(inherits=active, route_type='produce_produce')
        pack_pack = Statement(inherits=active, route_type='pack_pack')
        scrap_scrap = Statement(inherits=active, route_type='scrap_scrap')
        repair_repair = Statement(inherits=active, route_type='repair_repair')
        check_check = Statement(inherits=active, route_type='check_check')

        produce_stock = Statement(inherits=active, route_type='produce_stock')
        produce_pack = Statement(inherits=active, route_type='produce_pack')
        stock_produce = Statement(inherits=active, route_type='stock_produce')
        stock_pack = Statement(inherits=active, route_type='stock_pack')
        pack_stock = Statement(inherits=active, route_type='pack_stock')
        pack_produce = Statement(inherits=active, route_type='pack_produce')
        stock_check = Statement(inherits=active, route_type='stock_check')

        produce_customer = Statement(inherits=active, route_type='produce_customer')
        stock_customer = Statement(inherits=active, route_type='stock_customer')
        pack_customer = Statement(inherits=active, route_type='pack_customer')

        supplier_stock = Statement(inherits=active, route_type='supplier_stock')
        supplier_pack = Statement(inherits=active, route_type='supplier_pack')
        supplier_produce = Statement(inherits=active, route_type='supplier_produce')

        repair_stock = Statement(inherits=active, route_type='repair_stock')
        repair_customer = Statement(inherits=active, route_type='repair_customer')
        repair_pack = Statement(inherits=active, route_type='repair_pack')
        repair_produce = Statement(inherits=active, route_type='repair_produce')
        repair_check = Statement(inherits=active, route_type='repair_check')

        stock_repair = Statement(inherits=active, route_type='stock_repair')
        customer_repair = Statement(inherits=active, route_type='customer_repair')
        pack_repair = Statement(inherits=active, route_type='pack_repair')
        produce_repair = Statement(inherits=active, route_type='produce_repair')
        check_repair = Statement(inherits=active, route_type='check_repair')


    @classmethod
    def get_default_route(cls, warehouse, route_type):
        """
        get the default route which has the smallest sequence in the warehouse
        :param warehouse: stock.Warehouse instance
        :param route_type: string
        :return: stock.Route instance
        """
        return cls.get_state_instance(route_type, cls.objects.filter(warehouse=warehouse, sequence=0))

    def next_route_setting(self, now_route_setting=None, reverse=False):
        """
        get the next zone setting of the route after now zone setting,
        when reverse is True,return the previous zone setting of the route
        :param now_route_setting: stock.RouteSetting instance
        :param reverse: boolean
        :return: stock.RouteSetting instance
        """
        settings = self.routesetting_set.all()
        if not reverse:
            if now_route_setting:
                return settings.filter(sequence__gt=now_route_setting.sequence).first()
            return self.initial_setting
        else:
            if now_route_setting:
                return settings.filter(sequence__lt=now_route_setting.sequence).order_by('-sequence').first()
            return self.end_setting

    def sync_setting_and_type(self):
        with transaction.atomic():
            initial_setting = self.routesetting_set.first()
            end_setting = self.routesetting_set.last()
            if initial_setting and end_setting:
                route_type = '{}_{}'.format(
                    initial_setting.location.zone,
                    end_setting.location.zone
                )
            else:
                route_type = None
            self.initial_setting = initial_setting
            self.end_setting = end_setting
            self.route_type = route_type
            self.save()
            return self


class RouteSetting(models.Model, StateMachine):
    """
    the setting of location config the route's location chain
    """

    name = models.CharField(
        _('name'),
        null=False,
        blank=False,
        max_length=60,
        help_text=_('the name of location setting')
    )

    route = ActiveLimitForeignKey(
        'django_stock.Route',
        null=False,
        blank=False,
        verbose_name=_('route'),
        help_text=_('the route of location to chain together')
    )

    location = ActiveLimitForeignKey(
        'django_stock.Location',
        null=False,
        blank=False,
        verbose_name=_('limit location'),
        help_text=_("""
        if the location is virtual,the location item move to must be child of this,
        if the location is not virtual,the location item must move to this location
        """)
    )

    sequence = models.PositiveSmallIntegerField(
        _('sequence'),
        null=False,
        blank=False,
        default=0,
        help_text=_('the order of the location in route')
    )

    def __str__(self):
        return '{}/{}/{}'.format(self.route, self.location, self.sequence)

    class Meta:
        verbose_name = _('route setting')
        verbose_name_plural = _('route settings')
        unique_together = (
            ('route', 'sequence'),
            ('route', 'name')
        )
        ordering = ('sequence',)

    class States:
        active = Statement(Q(route__warehouse=F('location__warehouse')))
        initial = Statement(Q(route__initial_setting__pk=F('pk')), inherits=active)
        end = Statement(Q(route__end_setting__pk=F('pk')), inherits=active)


class Procurement(BaseModel):
    """
    procurement is the requirement of stock item from the location,
    it makes a series of move according to the route
    """
    warehouse = ActiveLimitForeignKey(
        'django_stock.Warehouse',
        null=False,
        blank=False,
        verbose_name=_('warehouse'),
        help_text=_('the warehouse of the procurement require')
    )

    user = models.ForeignKey(
        User,
        null=False,
        blank=False,
        verbose_name=_('user'),
        help_text=_('the user who ask the procurement')
    )

    require_procurements = models.ManyToManyField(
        'self',
        verbose_name=_('required procurements'),
        related_name='support_procurements',
        help_text=_('all of the required procurements must be done before this procurement change to confirmed status')
    )

    state = CancelableSimpleStateCharField(
        _('state'),
        help_text=_('procurement status')
    )

    def __str__(self):
        return 'procurement-{}'.format(self.pk)

    @property
    def doing_moves(self):
        """
        get the moves of doing status of this procurement
        :return:
        """
        return Move.get_state_queryset(
            'doing',
            Move.objects.filter(procurement_detail__procurement=self)
        )

    class Meta:
        verbose_name = _('procurement')
        verbose_name_plural = _('procurement')

    class States(BaseModel.States):
        active = BaseModel.States.active
        draft = Statement(inherits=active, state='draft')
        confirm_able = Statement(Q(procurementdetail__isnull=False), inherits=draft)
        confirmed = Statement(inherits=active, state='confirmed')
        done = Statement(inherits=active, state='done')
        cancel = Statement(inherits=active, state='cancel')

    def confirm(self):
        """
        change the procurement status from draft to confirmed
        :return: self
        """
        self.check_to_set_state('confirm_able', set_state='confirmed', raise_exception=True)
        return self

    def cancel(self):
        """
        change the procurement status from draft or confirmed to cancel
        :return: self
        """
        with transaction.atomic():
            self.check_to_set_state('draft', 'confirmed', set_state='cancel', raise_exception=True)
            for move in Move.get_state_queryset(
                    'cancel_able',
                    Move.objects.filter(procurement_detail__procurement=self)
            ):
                move.cancel()
            return self


class ProcurementDetail(models.Model, StateMachine):
    """
    the detail of procurement config what item user want to move
    """
    initial_location = ActiveLimitForeignKey(
        'django_stock.Location',
        null=True,
        blank=True,
        verbose_name=_('initial location'),
        related_name='initialprocurementdetail_set',
        validators=[StateInstanceValidator('no_virtual')],
        help_text=_('initial location for this detail,it must child of route initial location')
    )

    end_location = ActiveLimitForeignKey(
        'django_stock.Location',
        null=True,
        blank=True,
        verbose_name=_('initial location'),
        related_name='endprocurementdetail_set',
        validators=[StateInstanceValidator('no_virtual')],
        help_text=_('initial location for this detail,it must child of route initial location')
    )

    item = ActiveLimitForeignKey(
        'django_stock.Item',
        null=False,
        blank=False,
        verbose_name=_('item'),
        help_text=_('the item which will be move according to the route')
    )

    quantity = QuantityField(
        _('quantity'),
        null=False,
        blank=False,
        uom='django_product.template.uom',
        validators=[MinValueValidator(0)],
        help_text=_('the quantity of item will be move')
    )

    procurement = ActiveLimitForeignKey(
        'django_stock.Procurement',
        null=False,
        blank=False,
        verbose_name=_('procurement'),
        help_text=_('the procurement which detail belongs to')
    )

    route = ActiveLimitForeignKey(
        'django_stock.Route',
        null=False,
        blank=False,
        verbose_name=_('route'),
        help_text=_('the chain of location config by route which item will move according to')
    )

    direct_return = models.BooleanField(
        _('direct return status'),
        default=False,
        help_text=_('True means that items will return directly without other move in way')
    )

    def __str__(self):
        return '{}/{}'.format(str(self.procurement), str(self.item))

    class Meta:
        verbose_name = _('procurement detail')
        verbose_name_plural = _('procurement details')

    class States:
        start_able = Statement(
            Q(move__isnull=True) &
            Q(route__warehouse=F('procurement__warehouse')) & (
                Q(initial_location__isnull=True) |
                Q(initial_location=F('route__initial_setting__location')) |
                Q(initial_location__index__startswith=Concat(
                    F('route__initial_setting__location__index'),
                    F('route__initial_setting__location__pk'),
                    Value('-')
                ))
            ) & (
                Q(end_location__isnull=True) |
                Q(end_location=F('route__end_setting__location')) |
                Q(end_location__index__startswith=Concat(
                    F('route__end_setting__location__index'),
                    F('route__end_setting__location__pk'),
                    Value('-')
                ))
            ) &
            (Q(procurement__require_procurements__isnull=True) | Q(procurement__require_procurements__state='done'))
        )
        started = Statement(Q(move_set__isnull=False))

    @property
    def doing_move(self):
        """
        get all moves that which are create by this procurement detail
        :return: stock.Move instance
        """
        return Move.get_state_queryset('doing').get(procurement_detail=self)

    def start(self):
        """
        when procurement status become confirmed,procurement detail can create
        the first move according to the route
        :return: stock.Move instance
        """
        with transaction.atomic():
            self.check_states('start_able', raise_exception=True)
            self.procurement.check_states('confirmed', raise_exception=True)
            from_setting, to_setting = self.route.routesetting_set.all()[:2]
            from_location = (
                self.initial_location if from_setting.location.check_states('virtual') else from_setting.location
            )
            to_location = (
                (None if self.route.routesetting_set.count() != 2 else self.end_location)
                if to_setting.location.check_states('virtual') else to_setting.location
            )
            move = Move.objects.create(
                from_location=from_location,
                to_location=to_location,
                procurement_detail=self,
                from_route_setting=from_setting,
                to_route_setting=to_setting,
                quantity=self.quantity,
                state='draft'
            )
            move.confirm()
            return move