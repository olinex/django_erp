#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from decimal import Decimal as D

from django.conf import settings
from django.db import transaction
from django.db.models import Q, F
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.core.validators import MinValueValidator

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
    CancelableSimpleStateCharField
)
from common.state import Statement, StateMachine
from common.validators import NotZeroValidator

User =get_user_model()


class CacheItem(object):
    '''
    object reflect to stock item.
    as a manager which have all methods to control the quantity of item
    '''
    ALL = {'stock', 'check', 'pack', 'wait', 'deliver', 'midway'}
    SETTLED = {'customer'}
    TRANSPORTING = {'check', 'pack', 'wait', 'deliver', 'midway'}
    SCRAP = {'scrap'}
    REPAIR = {'repair'}
    CLOSEOUT = {'closeout'}

    ALL_ITEM_NAME_TEMPLATE = 'all_item_{}'
    LOCK_ITEM_NAME_TEMPLATE = 'lock_item_{}'
    NOW_ITEM_NAME_TEMPLATE = 'now_item_{}'
    QUANTITY_TYPE = {'now','lock','all'}

    def __init__(self, item):
        '''
        :param item: stock.Item instance
        '''
        self.item = item

    @classmethod
    def item_name(cls, item, quantity_type='now'):
        '''
        class method will return the key of item of zone
        :param item: stock.Item instance
        :return: string
        '''
        return getattr(cls,'{}_ITEM_NAME_TEMPLATE'.format(quantity_type.upper())).format(item.pk)


    def cache_name(self, quantity_type='now'):
        '''
        the name for redis as the key,each warehouse has it own cache name
        :return: string
        '''
        return self.item_name(self.item, quantity_type)

    @property
    def change_lock_name(self):
        return '{}_changed'.format(self.cache_name('now'))

    def get_quantity(self, *usages,quantity_type='now'):
        '''
        sum of item quantities figure out by set of usage
        :param usages: set or string
        :return: decimal
        '''

        redis = Redis()
        usages_set = set(usages)
        usage_list = set(Zone.States.USAGE_STATES.keys())
        if not usages_set.difference(usage_list):
            if quantity_type == 'now' and redis.get(self.change_lock_name):
                redis.zunionstore(
                    self.cache_name(quantity_type='now'),
                    keys={self.cache_name('all'):1, self.cache_name('lock'):-1}
                )
                redis.setnx(self.change_lock_name,0)
            return redis.zscore_sum(self.cache_name(quantity_type),*usages_set)
        raise NotInStates(_('usage'),_('unknown usage'))

    def all(self, quantity_type='now'):
        '''
        sum of item in all zones
        :return: decimal
        '''
        return self.get_quantity(*self.ALL,quantity_type=quantity_type)

    def settled(self, quantity_type='now'):
        '''
        sum of item in settled zones
        :return: decimal
        '''
        return self.get_quantity(*self.SETTLED,quantity_type=quantity_type)

    def transporting(self, quantity_type='now'):
        '''
        sum of item in transporting zones
        :return: decimal
        '''
        return self.get_quantity(*self.TRANSPORTING,quantity_type=quantity_type)

    def scrap(self, quantity_type='now'):
        '''
        sum of item in scrap zones
        :return: decimal
        '''
        return self.get_quantity(*self.SCRAP,quantity_type=quantity_type)

    def repair(self, quantity_type='now'):
        '''
        sum of item in repair zones
        :return: decimal
        '''
        return self.get_quantity(*self.REPAIR,quantity_type=quantity_type)

    def closeout(self, quantity_type='now'):
        '''
        sum of item in closeout zones
        :return: decimal
        '''
        return self.get_quantity(*self.CLOSEOUT,quantity_type=quantity_type)
    
    def _change(self, usage, quantity, quantity_type, pipe=None):
        '''
        increase of decrease the quantity of item in the zone of usage
        :param usage: string
        :param quantity: decimal
        :param pipe: pipeline of redis
        :return: 0 or 1
        '''
        if usage in Zone.States.USAGE_STATES.keys():
            if quantity_type in ('all','lock'):
                redis = pipe or Redis()
                result = redis.zincrby(self.cache_name(quantity_type=quantity_type), usage, quantity)
                if result:
                    redis.setnx(self.change_lock_name,1)
                return result
            raise AttributeError(quantity_type + _(' must be "all" or "lock".'))
        raise AttributeError(usage + _(' is unknown usage of zone.'))

    def refresh(self, usage, quantity, pipe=None):
        return self._change(usage,quantity,quantity_type='all',pipe=pipe)
    
    def lock(self, usage, quantity, pipe=None):
        return self._change(usage,quantity,quantity_type='lock',pipe=pipe)

    def sync(self):
        '''
        refresh all zones item quantity in the warehouse
        :return: self
        '''
        redis = Redis()
        pipe = redis.pipeline()
        watch_keys = Warehouse.leaf_child_locations_cache_name
        pipe.watch(watch_keys)
        pipe.delete(self.cache_name('now'),self.cache_name('all'),self.cache_name('lock'))
        for warehouse in Warehouse.get_state_queryset('active'):
            for usage in Zone.States.USAGE_STATES.keys():
                all_quantity = warehouse.get_item_quantity(
                    item=self.item,
                    usage=usage,
                    quantity_type='all',
                    pipe=pipe
                )
                pipe.zincrby(self.cache_name('all'), usage, all_quantity)
                lock_quantity = warehouse.get_item_quantity(
                    item=self.item,
                    usage=usage,
                    quantity_type='lock',
                    pipe=pipe
                )
                pipe.zincrby(self.cache_name('lock'), usage, lock_quantity)
        pipe.execute()
        return self


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

    @classmethod
    def location_name(cls,location):
        '''
        the name of location in redis as key
        :param location: stock.Location
        :return: string
        '''
        return cls.LOCATION_NAME_TEMPLATE.format(location.pk)

    @property
    def cache_name(self):
        '''
        the name of location in redis as key
        :return: string
        '''
        return self.location_name(self.location)
    
    def _change(self, item, quantity, quantity_type, pipe=None):
        '''
        increase of decrease the quantity of item in the location
        :param item: stock.Item instance
        :param quantity: decimal
        :param quantity_type: string
        :param pipe: redis pipeline
        :return: 0 or 1
        '''
        redis = pipe or Redis()
        return redis.zincrby(
            self.cache_name,
            CacheItem.item_name(item, quantity_type=quantity_type),
            quantity
        )

    def refresh(self, item, quantity, pipe=None):
        return self._change(item,quantity,quantity_type='all',pipe=pipe)

    def lock(self, item, quantity, pipe=None):
        return self._change(item,quantity,quantity_type='lock',pipe=pipe)

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
            CacheItem.item_name(item,quantity_type='lock')
        )


    def sync(self):
        '''
        refresh all item quantity in the location
        :return: self
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
        return self


class PackageType(BaseModel):
    '''
    the type of package which define it name,the name must be unique
    '''
    RELATED_NAME = 'package_types'

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
        related_name=RELATED_NAME,
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
        validators=[MinValueValidator(0)],
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
    RELATED_NAME = 'package_templates'

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
        related_name=RELATED_NAME,
        help_text=_('the package type of this template,constraint max number of item')
    )

    type_settings = models.ManyToManyField(
        'stock.PackageTypeItemSetting',
        blank=False,
        through='stock.PackageTemplateItemSetting',
        through_fields=('package_template', 'type_setting'),
        verbose_name=_('the type settings of package'),
        related_name=RELATED_NAME,
        help_text=_('the type settings of package which constraint max number of item')
    )

    def __str__(self):
        return str(self.package_type)

    class Meta:
        verbose_name = _('package template')
        verbose_name_plural = _('package templates')


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
        validators=[MinValueValidator(0)],
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


class PackageNode(TreeModel,StateMachine):
    '''
    package node,every node contain an package template
    '''

    template = ActiveLimitForeignKey(
        'stock.PackageTemplate',
        null=False,
        blank=False,
        verbose_name=_('package template'),
        related_name='package_nodes',
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


class Warehouse(BaseModel):
    '''
    warehouse have different zones
    '''
    RELATED_NAME = 'warehouses'

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
        related_name=RELATED_NAME,
        help_text=_('partner user can manage this warehouse')
    )

    address = ActiveLimitForeignKey(
        'account.Address',
        null=False,
        blank=False,
        verbose_name=_('address'),
        related_name=RELATED_NAME,
        help_text=_('the real address of warehouse')
    )

    def get_default_location(self, usage):
        '''
        get default location of the usage zone
        :param usage:usage string
        :return:stock.Location instance
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
        '''
        the default location of initial zone
        :return: stock.Location instance
        '''
        return self.get_default_location('initial')

    @property
    def scrap_location(self):
        '''
        the default location of scrap zone
        :return: stock.Location instance
        '''
        return self.get_default_location('scrap')

    @property
    def closeout_location(self):
        '''
        the default location of closeout zone
        :return: stock.Location instance
        '''
        return self.get_default_location('closeout')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('warehouse')
        verbose_name_plural = _('warehouse')

    def create_zones(self):
        '''
        create all zones of this warehouse,generally be called by create action in signal
        :return: self
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
            return self

    def create_default_routes(self):
        '''
        every zones in the warehouse has it's own routes
        :return: self
        '''
        with transaction.atomic():
            for route_type, explain in Route.ROUTE_TYPE:
                Route.objects.create(
                    warehouse=self,
                    name='default/{}/{}'.format(self, route_type),
                    route_type=route_type,
                    sequence=0
                )
            return self

    @property
    def leaf_child_locations(self):
        '''
        get all not virtual child locations of this warehouse
        :return: stock.Location queryset
        '''
        return Location.get_state_queryset('no_virtual').filter(zone__warehouse=self)

    @property
    def leaf_child_locations_cache_name(self):
        '''
        get all not virtual child location's cache name
        :return: list
        '''
        return [location.cache.cache_name for location in self.leaf_child_locations]

    def get_item_quantity(self, item, usage,quantity_type='now',pipe=None):
        '''
        return the item quantity in usage
        :param item: stock.Item instance
        :param usage: string of usage or 'all'
        :return: decimal
        '''
        if usage in Zone.States.USAGE_STATES.keys():
            zone = Zone.get_state_instance(usage)
            return zone.get_item_quantity(
                item=item,
                quantity_type=quantity_type,
                pipe=pipe
            )
        else:
            return D(0)


class Zone(BaseModel):
    '''
    zone in warehouse,every zone has it's own type
    '''
    RELATED_NAME = 'zones'
    LAYOUT_USAGE = (
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
        ('midway', _('zone for midway'))
    )
    INDIVISIBLE_USAGE = {'initial', 'closeout'}

    warehouse = ActiveLimitForeignKey(
        'stock.Warehouse',
        null=False,
        blank=False,
        verbose_name=_('warehouse'),
        related_name=RELATED_NAME,
        help_text=_('the warehouse zone belongs to')
    )

    usage = models.CharField(
        _('usage'),
        null=False,
        blank=False,
        choices=LAYOUT_USAGE,
        max_length=30,
        default='container',
        help_text=_('the usage of zone')
    )

    root_location = ActiveLimitForeignKey(
        'stock.Location',
        null=True,
        blank=True,
        verbose_name=_('root location'),
        related_name='self_zone',
        help_text=_('the location for zone itself')
    )

    def __str__(self):
        return str(self.warehouse) + '/' + self.usage

    class Meta:
        verbose_name = _('zone')
        verbose_name_plural = _('zones')
        unique_together = (
            ('warehouse', 'usage'),
        )

    class States(BaseModel.States):
        active = Statement(
            Q(warehouse__is_active=True) & Q(warehouse__is_delete=False),
            inherits=BaseModel.States.active
        )
        stock = Statement(inherits=active, usage='stock')
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

    def get_item_quantity(self, item, quantity_type='now',pipe=None):
        '''
        get quantity of item in this zone
        :param item: stock.item instance
        :return: decimal
        '''
        return self.root_location.get_item_quantity(
            item,
            quantity_type=quantity_type,
            pipe=pipe
        )


class Location(BaseModel, TreeModel):
    '''
    the location in warehouse
    '''

    zone = ActiveLimitForeignKey(
        'stock.Zone',
        null=False,
        blank=False,
        verbose_name=_('zone'),
        related_name='locations',
        help_text=_('the zone which contain this location')
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
        '''
        get the name of location key in redis
        :return: string
        '''
        return CacheLocation.location_name(self)


    def __str__(self):
        return str(self.zone) + '(X:{},Y:{},Z:{})'.format(
            self.x,
            self.y,
            self.z
        )

    class Meta:
        verbose_name = _('warehouse location')
        verbose_name_plural = _('warehouse locations')
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
        '''
        change this location's parent location
        the parent location must be virtual
        this location must be active
        :param node: stock.Location instance
        :return: self
        '''
        if self.zone == node.zone:
            redis = Redis()
            node.check_states('virtual', raise_exception=True)
            self.check_states('active', raise_exception=True)
            return super(Location, self).change_parent_node(node)
        raise NotInStates(_('other'), _("parent node's zone must equal to this location"))

    @property
    def leaf_child_locations(self):
        '''
        get all no virtual location
        :return: stock.Location instance
        '''
        return self.__class__.get_state_queryset('no_virtual', self.all_child_nodes)

    @property
    def leaf_child_location_cache_name(self):
        '''
        get the list of all not virtual child location's cache name
        :return: list
        '''
        return [location.location_name for location in self.leaf_child_locations]

    @property
    def cache(self):
        '''
        :return: stock.CacheLocation instance
        '''
        if not hasattr(self, '__cache'):
            self.__cache = CacheLocation(location=self)
        return self.__cache

    def in_sum(self, item):
        '''
        get move in number of item to this location
        :param item: stock.Item instance
        :return: decimal
        '''
        from django.db.models import Sum
        return Move.get_state_queryset('done').filter(
            to_location=self,
            procurement_detail__item=item
        ).aggregate(in_sum=Sum('quantity'))['in_sum'] or D(0)

    def out_sum(self, item):
        '''
        get move out number of item from this location
        :param item: stock.Item instance
        :return: decimal
        '''
        from django.db.models import Sum
        return Move.get_state_queryset('done').filter(
            from_location=self,
            procurement_detail__item=item
        ).aggregate(out_sum=Sum('quantity'))['out_sum'] or D(0)
    
    def get_item_quantity(self, item, quantity_type='now', pipe=None):
        '''
        get the quantity of item in type
        :param item: stock.Item instance
        :param quantity_type: string
        :return: decimal
        '''
        redis = pipe or Redis()
        if self.check_states('virtual'):
            redis.zunionstore(
                dest=self.location_name,
                keys=self.leaf_child_location_cache_name,
            )
        if quantity_type != 'now':
            result = redis.zscore(
                self.location_name,
                CacheItem.item_name(item, quantity_type)
            )
            return D(result) if result is not None else D(0)
        else:
            all_result = redis.zscore(
                self.location_name,
                CacheItem.item_name(item, 'all')
            )
            lock_result = redis.zscore(
                self.location_name,
                CacheItem.item_name(item, 'lock')
            )
            all_result = D(all_result) if all_result is not None else D(0)
            lock_result = D(lock_result) if lock_result is not None else D(0)
            return all_result - lock_result


class Move(BaseModel):
    '''
    the move recording the start position and end position
    '''

    from_location = LocationForeignKey(
        null=False,
        blank=False,
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
        'stock.ProcurementDetail',
        blank=False,
        verbose_name=_('procurement detail'),
        related_name='moves',
        help_text=_('the procurement detail which create this move')
    )

    zone_setting = models.ForeignKey(
        'stock.RouteZoneSetting',
        null=False,
        blank=False,
        verbose_name=_('route zone setting'),
        related_name='moves',
        help_text=_('moves will be create according to the route,each move has it own zone setting')
    )

    quantity = QuantityField(
        _('zone'),
        null=False,
        blank=False,
        uom='item.instance.uom',
        validators=[MinValueValidator(0)],
        help_text=_('the number of item was moved')
    )

    is_return = models.BooleanField(
        _('return status'),
        default=False,
        help_text=_('True means item will be move back to the origin location')
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
        unique_together = ('procurement_detail', 'zone_setting', 'is_return')

    class States(BaseModel.States):
        active = BaseModel.States.active
        draft = Statement(inherits=active, state='draft')
        confirmed = Statement(inherits=active, state='confirmed')
        doing = Statement(Q(state='draft') | Q(state='confirmed'), inherits=active)
        done_able = Statement(Q(to_location__zone=F('zone_setting__zone')),inherits=confirmed)
        done = Statement(inherits=active, state='done')
        cancel_able = Statement(Q(procurement_detail__procurement__state='cancel'),inherits=draft)
        cancel = Statement(inherits=active,state='cancel')
        is_return = Statement(inherits=active, is_return=True)
        no_return = Statement(inherits=active, is_return=False)

    def refresh_lock_item_quantity(self,pipe=None,reverse=False):
        '''
        increase/decrease the lock number of item in the zone
        :return: 0 or 1
        '''
        return self.from_location.cache.lock(
            item=self.procurement_detail.item,
            quantity=self.quantity if not reverse else - self.quantity,
            pipe=pipe
        )

    def refresh_item_quantity(self):
        '''
        increase/decrease the number of item in the zone
        :return: 0 or 1
        '''
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
        self.refresh_lock_item_quantity(pipe=pipe,reverse=True)
        if self.from_location.zone.usage != self.to_location.zone.usage:
            self.procurement_detail.item.cache.refresh(self.from_location.zone.usage, -self.quantity, pipe=pipe)
            self.procurement_detail.item.cache.refresh(self.to_location.zone.usage, self.quantity, pipe=pipe)
        pipe.execute()

    def confirm(self):
        '''
        change move status from draft to confirmed and increase the lock quantity of item in redis
        :return: self
        '''
        with transaction.atomic():
            self.check_to_set_state('draft', set_state='confirmed', raise_exception=True)
            self.refresh_lock_item_quantity()
            return self

    def cancel(self):
        '''
        change move status from cancel_able to cancel and
        :return:
        '''
        with transaction.atomic():
            self.check_to_set_state('cancel_able', set_state='cancel', raise_exception=True)
            self.refresh_lock_item_quantity(reverse=True)
            move = self.get_next_move()[0]
            if move:
                move.save()
                self.to_move = move
                self.save()
                move.confirm()
            return self

    def get_next_move(self):
        '''
        get the next move of this move
        :return: (stock.Move instance,boolean,boolean)
        '''
        is_cancel = self.check_states('cancel')
        procurement_cancel = self.procurement_detail.procurement.check_states('cancel')
        next_zone_setting = self.procurement_detail.route.next_zone_setting(
            now_zone_setting=(
                None if (procurement_cancel and self.procurement_detail.direct_return)
                else self.zone_setting
            ),
            reverse=procurement_cancel
        )
        if is_cancel:
            next_zone_setting = self.procurement_detail.route.next_zone_setting(
                now_zone_setting=next_zone_setting,
                reverse=procurement_cancel
            )
        if next_zone_setting:
            return (Move(
                from_location=self.to_location if not is_cancel else self.from_location,
                to_location=None,
                zone_setting=next_zone_setting,
                procurement_detail=self.procurement_detail,
                quantity=self.quantity,
                is_return=procurement_cancel,
                state='draft'
            ),is_cancel,procurement_cancel)
        return (None,is_cancel,procurement_cancel)


    def done(self):
        '''
        完成库存移动的动作,并自动根据需求状态和路线指定下一个库存移动
        1 需求尚未完成时,根据当前移动的路线区域获取下一个路线区域,若存在下一个路线区域且传入库位的区域与之相同,则完成移动并创建移动
        2 需求尚未完成时,根据当前移动的路线区域获取下一个路线区域,若存在下一个路线区域且传入库位的区域与之不同,则抛出错误
        3 需求尚未完成时,根据当前移动的路线区域获取下一个路线区域,若不存在下一个路线区域且传入了库位,则抛出错误
        4 需求尚未完成时,根据当前移动的路线区域获取下一个路线区域,若不存在下一个路线区域且未传入库位,
          则完成移动并检查需求下的所有移动是否均已完成,若完成则将需求置于完成状态
        :return: self
        '''
        with transaction.atomic():
            self.check_to_set_state('confirmed', set_state='done', raise_exception=True)
            procurement = self.procurement_detail.procurement
            move,cancel_status,procurement_cancel = self.get_next_move()
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
                moves__isnull=True,procurement=procurement).exists():
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

class StockOrder(BaseModel):
    '''
    the abstract order to manage stock operation
    '''
    @property
    def state(self):
        '''
        the status of order,same as the procurement status
        :return: string
        '''
        if self.procurement:
            return self.procurement.state
        return 'draft'

    class Meta:
        abstract = True

    class States(BaseModel.States):
        draft = Statement(Q(procurement__isnull=True),inherits=BaseModel.States.active)
        confirmed = Statement(Q(procurement__state='confirmed'),inherits=BaseModel.States.active)
        done = Statement(Q(procurement__state='done'),inherits=BaseModel.States.active)

    def confirm(self):
        '''
        change the status of procurement from draft to confirmed
        :return: self
        '''
        with transaction.atomic():
            self.check_states('draft',raise_exception=True)
            self.procurement = Procurement.objects.create(user=self.create_user)
            self.save()
            for line in self.lines.all():
                line.create_procurement_detail()
            self.procurement.confirm()
            return self


class PackOrder(StockOrder):
    '''
    the order to manage packing operation
    '''
    RELATED_NAME = 'pack_orders'
    SINGLE_RELATED_NAME = 'pack_order'

    procurement = ActiveLimitOneToOneField(
        'stock.Procurement',
        null=True,
        blank=True,
        verbose_name=_('procurement'),
        related_name=SINGLE_RELATED_NAME,
        help_text=_('the procurement about this order')
    )

    location = ActiveLimitForeignKey(
        'stock.Location',
        null=False,
        blank=False,
        verbose_name=_('location'),
        related_name=RELATED_NAME,
        help_text=_('the location to make operation')
    )

    create_user = models.ForeignKey(
        User,
        null=False,
        blank=False,
        verbose_name=_('create user'),
        related_name=RELATED_NAME,
        help_text=_('the user who create this pack order')
    )

    is_pack = models.BooleanField(
        _('pack status'),
        default=True,
        help_text=_('True means the operation is packing,False means the operation is unpacking')
    )

    package_nodes = models.ManyToManyField(
        'stock.PackageNode',
        through='stock.PackOrderLine',
        through_fields=('order', 'package_node'),
        verbose_name=_('package nodes'),
        related_name='pack_orders',
        help_text=_('all kinds of package node will be pack/unpack')
    )

    def __str__(self):
        return 'pack-order-{}-{}'.format(self.location,self.pk)

    class Meta:
        verbose_name = _('pack order')
        verbose_name_plural = _('pack orders')


class PackOrderLine(models.Model, StateMachine):
    '''
    the pack order line bind to procurement details
    '''

    order = ActiveLimitForeignKey(
        'stock.PackOrder',
        null=False,
        blank=False,
        verbose_name=_('pack order'),
        related_name='lines',
        help_text=_('pack order')
    )

    package_node = models.ForeignKey(
        'stock.PackageNode',
        null=False,
        blank=False,
        verbose_name=_('package node'),
        related_name='pack_order_lines',
        limit_choices_to=PackageNode.States.root.query,
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
        'stock.ProcurementDetail',
        through='stock.PackOrderLineProcurementDetailSetting',
        through_fields=('line', 'detail'),
        verbose_name=_('procurement details'),
        related_name='pack_order_lines',
        help_text=_('the procurement details about the package node')
    )

    @property
    def package_detail(self):
        '''
        the procurement detail about package node
        :return: stock.ProcurementDetail instance
        '''
        return self.procurement_details.get(item=self.package_node.item)

    @property
    def item_details(self):
        '''
        the procurement details about stock item
        :return: stock.ProcurementDetail queryset
        '''
        return self.procurement_details.exclude(item=self.package_node.item)

    def __str__(self):
        return '{}/{}'.format(self.order, self.package_node)

    class Meta:
        verbose_name = _('pack order line')
        verbose_name_plural = _('pack order lines')
        unique_together = ('order', 'package_node')

    def _create_item_detail_settings(self):
        '''
        create every package template's items
        :return: self
        '''
        warehouse = self.order.location.zone.warehouse
        route = Route.get_default_route(warehouse, 'pack_closeout' if self.order.is_pack else 'closeout_pack')
        for setting in self.package_node.template.template_settings.all():
            detail = ProcurementDetail.objects.create(
                procurement=self.order.procurement,
                item=setting.type_setting.item,
                quantity=setting.quantity * self.quantity,
                route=route
            )
            PackOrderLineProcurementDetailSetting.objects.create(
                line=self,
                node=self.package_node,
                template_setting=setting,
                detail=detail
            )
        for node in self.package_node.all_child_nodes:
            for setting in node.template.template_settings.all():
                detail = ProcurementDetail.objects.create(
                    procurement=self.order.procurement,
                    item=setting.type_setting.item,
                    quantity=setting.quantiy * self.quantity,
                    route=route
                )
                PackOrderLineProcurementDetailSetting.objects.create(
                    line=self,
                    detail=detail,
                    node=node,
                    template_setting=setting
                )
        return self

    def _create_package_detail_setting(self):
        '''
        create every package node
        :return: self
        '''
        warehouse = self.order.location.zone.warehouse
        route = Route.get_default_route(warehouse, 'closeout_pack' if self.order.is_pack else 'pack_closeout')
        detail = ProcurementDetail.objects.create(
            procurement=self.order.procurement,
            item=self.package_node.item,
            quantity=self.quantity,
            route=route
        )
        PackOrderLineProcurementDetailSetting.objects.create(
            line=self,
            detail=detail,
            node=self.package_node,
            template_setting=None
        )
        return self

    def create_procurement_detail(self):
        with transaction.atomic():
            self._create_item_detail_settings()
            self._create_package_detail_setting()

    def done(self):
        '''
        complete the item procurement detail and package node procurement detail
        :return: self
        '''
        with transaction.atomic():
            pack_location = self.order.location
            closeout_location = pack_location.zone.warehouse.closeout_location
            if not self.order.is_pack:
                pack_location, closeout_location = closeout_location, pack_location
            for detail in self.item_details:
                detail.start(pack_location, closeout_location).done()
            self.package_detail.start(closeout_location, pack_location).done()
            return self


class PackOrderLineProcurementDetailSetting(models.Model):
    '''
    config the one to many relationship with pack order line and procurement detail
    '''
    RELATED_NAME = 'pack_detail_settings'
    SINGLE_RELATED_NAME = 'pack_detail_setting'

    line = models.ForeignKey(
        'stock.PackOrderLine',
        null=False,
        blank=False,
        verbose_name=_('pack order line'),
        related_name=RELATED_NAME,
        help_text=_('the pack order line which procurement detail bind with')
    )

    detail = models.OneToOneField(
        'stock.ProcurementDetail',
        null=False,
        blank=False,
        verbose_name=_('procurement detail'),
        related_name=SINGLE_RELATED_NAME,
        help_text=_('procurement detail bind with pack order line which config the package node')
    )

    node = ActiveLimitForeignKey(
        'stock.PackageNode',
        null=False,
        blank=False,
        verbose_name=_('package node'),
        related_name=RELATED_NAME,
        help_text=_('package node which procurement detail was created by')
    )

    template_setting = models.ForeignKey(
        'stock.PackageTemplateItemSetting',
        null=True,
        blank=True,
        verbose_name=_('package template setting'),
        related_name=RELATED_NAME,
        help_text=_('package template setting about packing item')
    )

    def __str__(self):
        return '{}/{}'.format(self.line, self.detail)

    class Meta:
        verbose_name = _('pack order line - procurement detail relationship')
        verbose_name_plural = _('pack order line - procurement detail relationships')


class ScrapOrder(StockOrder):
    '''the order to manage scrap operation'''
    RELATED_NAME = 'scrap_orders'
    SINGLE_RELATED_NAME = 'scrap_order'

    procurement = ActiveLimitOneToOneField(
        'stock.Procurement',
        null=True,
        blank=True,
        verbose_name=_('procurement'),
        related_name=SINGLE_RELATED_NAME,
        help_text=_('the procurement about this order')
    )

    location = ActiveLimitForeignKey(
        'stock.Location',
        null=False,
        blank=False,
        verbose_name=_('location'),
        related_name=RELATED_NAME,
        help_text=_('the location to make operation')
    )

    create_user = models.ForeignKey(
        User,
        null=False,
        blank=False,
        verbose_name=_('create user'),
        related_name=RELATED_NAME,
        help_text=_('the user who create this pack order')
    )

    procurement_details = models.ManyToManyField(
        'stock.ProcurementDetail',
        through='stock.ScrapOrderLine',
        through_fields=('order', 'procurement_detail'),
        verbose_name=_('procurement details'),
        related_name=RELATED_NAME,
        help_text=_('scrap procurement details makes by this order')
    )

    def __str__(self):
        return 'scrap-order-{}-{}'.format(self.location,self.pk)

    class Meta:
        verbose_name = _('scrap order')
        verbose_name_plural = _('scrap orders')


class ScrapOrderLine(models.Model, StateMachine):
    '''
    the scrap order line bind to procurement detail
    '''

    order = models.ForeignKey(
        'stock.ScrapOrder',
        null=False,
        blank=False,
        verbose_name=_('scrap order'),
        related_name='lines',
        help_text=_('scrap order')
    )

    item = ActiveLimitForeignKey(
        'stock.Item',
        null=False,
        blank=False,
        verbose_name=_('item'),
        related_name='scrap_order_lines',
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

    procurement_detail = models.OneToOneField(
        'stock.ProcurementDetail',
        null=True,
        blank=True,
        verbose_name=_('procurement detail'),
        related_name='scrap_order_lines',
        help_text=_('the procurement detail which order line bind with')
    )

    def __str__(self):
        return '{}/{}'.format(self.order, self.procurement_detail)

    class Meta:
        verbose_name = _('scrap order line'),
        verbose_name_plural = _('scrap order lines')

    def create_procurement_detail(self):
        '''
        create the scrap order line and procurement detail
        :return: stock.ScrapOrderLine instance
        '''
        with transaction.atomic():
            zone = self.order.location.zone
            route = Route.get_default_route(zone.warehouse, '{}_scrap'.format(zone.usage))
            self.procurement_detail = ProcurementDetail.objects.create(
                procurement=self.order.procurement,
                item=self.item,
                quantity=self.quantity,
                route=route
            )
            self.save()
            return self

    def start(self):
        '''
        start moving the scrap procurement detail item
        :return:
        '''
        with transaction.atomic():
            from_location = self.order.location
            to_location = from_location.zone.warehouse.scrap_location
            self.procurement_detail.start(from_location, to_location)
            return self


class CloseoutOrder(StockOrder):
    '''
    the order to manage closeout operation
    '''
    RELATED_NAME= 'closeout_orders'
    SINGLE_RELATED_NAME = 'closeout_order'

    procurement = ActiveLimitOneToOneField(
        'stock.Procurement',
        null=True,
        blank=True,
        verbose_name=_('procurement'),
        related_name=SINGLE_RELATED_NAME,
        help_text=_('the procurement about this order')
    )

    location = ActiveLimitForeignKey(
        'stock.Location',
        null=False,
        blank=False,
        verbose_name=_('location'),
        related_name=RELATED_NAME,
        help_text=_('the location to make operation')
    )

    create_user = models.ForeignKey(
        User,
        null=False,
        blank=False,
        verbose_name=_('create user'),
        related_name=RELATED_NAME,
        help_text=_('the user who create this pack order')
    )

    procurement_details = models.ManyToManyField(
        'stock.ProcurementDetail',
        through='stock.CloseoutOrderLine',
        through_fields=('order', 'procurement_detail'),
        verbose_name=_('procurement details'),
        related_name=RELATED_NAME,
        help_text=_('procurement details about closeout operation')
    )

    def __str__(self):
        return 'closeout-order-{}'.format(self.location,self.pk)

    class Meta:
        verbose_name = _('closeout order')
        verbose_name_plural = _('closeout orders')


class CloseoutOrderLine(models.Model):
    '''
    order line of closeout
    '''
    order = models.ForeignKey(
        'stock.CloseoutOrder',
        null=False,
        blank=False,
        verbose_name=_('closeout order'),
        related_name='lines',
        help_text=_('closeout order')
    )

    procurement_detail = models.OneToOneField(
        'stock.ProcurementDetail',
        null=True,
        blank=True,
        verbose_name=_('procurement detail'),
        related_name='closeout_order_lines',
        help_text=_('procurement detail of closeout')
    )

    item = ActiveLimitForeignKey(
        'stock.Item',
        null=False,
        blank=False,
        verbose_name=_('item'),
        related_name='closeout_order_lines',
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
        return '{}/{}'.format(self.order, self.procurement_detail)

    class Meta:
        verbose_name = _('closeout order line')
        verbose_name_plural = _('closeout order lines')

    def create_procurement_detail(self):
        '''
        create closeout order line and procurement detail
        :return: stock.CloseoutOrderLine instance
        '''
        with transaction.atomic():
            zone = self.order.location.zone
            route_label ='closeout_{}' if self.quantity > 0 else '{}_closeout'
            route = Route.get_default_route(zone.warehouse, route_label.format(zone.usage))
            self.procurement_detail = ProcurementDetail.objects.create(
                procurement=self.order.procurement,
                item=self.item,
                quantity=abs(self.quantity),
                route=route
            )
            self.save()
            return self

    def start(self):
        '''
        start to move closeout procurement detail item
        :return:
        '''
        with transaction.atomic():
            from_location = self.order.location
            to_location = from_location.zone.warehouse.closeout_location
            if self.quantity > 0:
                self.procurement_detail.start(to_location, from_location)
            else:
                self.procurement_detail.start(from_location, to_location)
            return self

class InnerOrder(BaseModel):
    ''''''
    RELATED_NAME = 'inner_orders'

    procurement = ActiveLimitOneToOneField(
        'stock.Procurement',
        null=False,
        blank=False,
        verbose_name=_('procurement'),
        related_name=RELATED_NAME,
        help_text=_('the procurement about this order')
    )

    @classmethod
    def create(cls, user):
        '''
        create the inner order and procurement
        :param user: auth.User instance
        :return: stock.InnerOrder instance
        '''
        with transaction.atomic():
            procurement = Procurement.objects.create(user=user)
            return cls.objects.create(procurement=procurement)

    def confirm(self):
        '''
        change the status of procurement from draft to confirmed
        :return: self
        '''
        with transaction.atomic():
            self.procurement.confirm()
            return self

    class Meta:
        verbose_name = _('inner order')
        verbose_name_plural = _('inner orders')

    def __str__(self):
        return 'inner-order-{}'.format(self.pk)

class InnerOrderLine(models.Model,StateMachine):
    '''
    inner order line for make moving according inner route
    '''
    order = ActiveLimitForeignKey(
        'stock.InnerOrder',
        null=False,
        blank=False,
        verbose_name=_('inner order'),
        related_name='lines',
        help_text=_('inner order which this order line belongs to')
    )

    procurement_detail = models.OneToOneField(
        'stock.ProcurementDetail',
        null=False,
        blank=False,
        verbose_name=_('procurement detail'),
        related_name='inner_order_lines',
        help_text=_('the procurement detail which order line bind with')
    )

    def __str__(self):
        return '{}/{}'.format(self.order, self.procurement_detail)

    class Meta:
        verbose_name = _('inner order line'),
        verbose_name_plural = _('inner order lines')

    def start(self):
        '''
        start moving the inner procurement detail item
        :return: self
        '''
        with transaction.atomic():
            from_location = self.order.scrap_location
            to_location = from_location.zone.warehouse.scrap_location
            self.procurement_detail.start(from_location,to_location)
            return self

class Route(BaseModel):
    ROUTE_TYPE = (
        ('produce_stock',       _('produce to stock route')),
        ('produce_customer',    _('produce to customer route')),
        ('produce_pack',        _('produce to pack route')),
        ('produce_closeout',    _('produce to closeout route')),
        ('produce_produce',     _('produce to produce route')),
        ('produce_repair',      _('produce to repair route')),
        ('produce_scrap',       _('produce to scrap route')),

        ('stock_stock',         _('stock to stock route')),
        ('stock_customer',      _('stock to customer route')),
        ('stock_pack',          _('stock to pack route')),
        ('stock_closeout',      _('stock to closeout route')),
        ('stock_produce',       _('stock to produce route')),
        ('stock_repair',        _('stock to repair route')),
        ('stock_scrap',         _('stock to scrap route')),

        ('pack_stock',          _('pack to stock route')),
        ('pack_customer',       _('pack to customer route')),
        ('pack_pack',           _('pack to pack route')),
        ('pack_closeout',       _('pack to closeout route')),
        ('pack_produce',        _('pack to produce route')),
        ('pack_repair',         _('pack to repair route')),
        ('pack_scrap',          _('pack to scrap route')),

        ('closeout_stock',      _('closeout to stock route')),
        ('closeout_pack',       _('closeout to pack route')),
        ('closeout_produce',    _('closeout to produce route')),

        ('supplier_stock',      _('supplier to stock route')),
        ('supplier_pack',       _('supplier to pack route')),
        ('supplier_produce',    _('supplier to produce route')),

        ('repair_stock',        _('repair to stock route')),
        ('repair_customer',     _('repair to customer route')),
        ('repair_pack',         _('repair to pack route')),
        ('repair_produce',      _('repair to produce route')),
        ('repair_scrap',        _('repair to scrap route')),

        ('scrap_repair',        _('scrap to repair route')),
        ('customer_repair',     _('customer to repair route')),
        ('check_repair',        _('check to repair route')),
        ('check_scrap',         _('check to scrap route')),
    )
    '''
    the route of zone to chain together
    '''

    name = models.CharField(
        _('name'),
        null=False,
        blank=False,
        unique=True,
        max_length=190,
        help_text=_('the name of route')
    )

    warehouse = ActiveLimitForeignKey(
        'stock.Warehouse',
        null=False,
        blank=False,
        verbose_name=_('warehouse'),
        related_name='routes',
        help_text=_('the warehouse which route belongs to')
    )

    route_type = models.CharField(
        _('route type'),
        null=False,
        blank=False,
        choices=ROUTE_TYPE,
        max_length=20,
        help_text=_('the type of route')
    )

    zones = models.ManyToManyField(
        'stock.Zone',
        through='stock.RouteZoneSetting',
        through_fields=('route', 'zone'),
        blank=False,
        verbose_name=_('zones'),
        related_name='routes',
        help_text=_('the zones chain to be route')
    )

    users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=False,
        verbose_name=_('users'),
        related_name='usable_routes',
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
        '''
        the count of route's zones
        :return: int
        '''
        return RouteZoneSetting.objects.filter(route=self).count()

    @property
    def initial_zone(self):
        '''
        get the first zone of this route
        :return: stock.Zone instance
        '''
        return Zone.objects.get(warehouse=self.warehouse, usage=self.route_type.split('_')[0])

    @property
    def end_zone(self):
        '''
        get the last zone of this route
        :return: stock.Zone instance
        '''
        return Zone.objects.get(warehouse=self.warehouse, usage=self.route_type.split('_')[1])

    @property
    def initial_setting(self):
        '''
        get the first route zone setting contain the first zone
        :return: stock.RouteZoneSetting instance
        '''
        return RouteZoneSetting.objects.filter(route=self).first()

    @property
    def end_setting(self):
        '''
        get the last route zone setting contain the last zone
        :return: stock.RouteZoneSetting instance
        '''
        return RouteZoneSetting.objects.filter(route=self).last()

    class Meta:
        verbose_name = _('route')
        verbose_name_plural = _('routes')
        unique_together = ('warehouse', 'route_type', 'sequence')

    class States(BaseModel.States):
        OUTPUT_TYPE = {'produce_customer', 'stock_customer', 'pack_customer'}
        INPUT_TYPE = {'supplier_stock', 'supplier_stock', 'supplier_produce'}
        INNER_TYPE = {
            'produce_stock', 'produce_pack', 'produce_produce',
            'stock_produce','stock_pack','stock_stock',
            'pack_stock','pack_produce','pack_pack'
        }
        SCRAP_TYPE = {
            'scrap_repair','repair_scrap',
            'stock_scrap','pack_scrap','produce_scrap','check_scrap'
        }
        CLOSEOUT_TYPE = {
            'closeout_stock','stock_closeout',
            'closeout_pack','pack_closeout',
            'closeout_produce','produce_closeout'
        }

        active = BaseModel.States.active
        produce_stock = Statement(inherits=active, route_type='produce_stock')
        produce_customer = Statement(inherits=active, route_type='produce_customer')
        produce_pack = Statement(inherits=active, route_type='produce_pack')
        produce_produce = Statement(inherits=active, route_type='produce_produce')
        produce_closeout = Statement(inherits=active, route_type='produce_closeout')
        produce_repair = Statement(inherits=active, route_type='produce_repair')
        produce_scrap = Statement(inherits=active, route_type='produce_scrap')

        stock_produce = Statement(inherits=active, route_type='stock_produce')
        stock_customer = Statement(inherits=active, route_type='stock_customer')
        stock_pack = Statement(inherits=active, route_type='stock_pack')
        stock_stock = Statement(inherits=active, route_type='stock_stock')
        stock_closeout = Statement(inherits=active, route_type='stock_closeout')
        stock_repair = Statement(inherits=active, route_type='stock_repair')
        stock_scrap = Statement(inherits=active, route_type='stock_scrap')

        pack_stock = Statement(inherits=active, route_type='pack_stock')
        pack_customer = Statement(inherits=active, route_type='pack_customer')
        pack_produce = Statement(inherits=active, route_type='pack_produce')
        pack_pack = Statement(inherits=active, route_type='pack_pack')
        pack_closeout = Statement(inherits=active, route_type='pack_closeout')
        pack_repair = Statement(inherits=active, route_type='pack_repair')
        pack_scrap = Statement(inherits=active, route_type='pack_scrap')

        supplier_stock = Statement(inherits=active, route_type='supplier_stock')
        supplier_pack = Statement(inherits=active, route_type='supplier_pack')
        supplier_produce = Statement(inherits=active, route_type='supplier_produce')

        closeout_stock = Statement(inherits=active, route_type='closeout_stock')
        closeout_pack = Statement(inherits=active, route_type='closeout_pack')
        closeout_produce = Statement(inherits=active, route_type='closeout_produce')

        customer_repair = Statement(inherits=active, route_type='customer_repair')
        scrap_repair = Statement(inherits=active, route_type='scrap_repair')
        check_repair = Statement(inherits=active, route_type='check_repair')
        check_scrap = Statement(inherits=active, route_type='check_repair')

        repair_customer = Statement(inherits=active, route_type='repair_customer')
        repair_stock = Statement(inherits=active, route_type='repair_stock')
        repair_pack = Statement(inherits=active, route_type='repair_pack')
        repair_produce = Statement(inherits=active, route_type='repair_produce')
        repair_scrap = Statement(inherits=active, route_type='repair_scrap')

        output = Statement(Q(route_type__in=OUTPUT_TYPE),inherits=active)
        input = Statement(Q(route_type__in=INPUT_TYPE),inherits=active)
        inner = Statement(Q(route_type__in=INNER_TYPE),inherits=active)


    @classmethod
    def get_default_route(cls, warehouse, route_type):
        '''
        get the default route which has the smallest sequence in the warehouse
        :param warehouse: stock.Warehouse instance
        :param route_type: string
        :return: stock.Route instance
        '''
        return cls.get_state_instance(route_type, cls.objects.filter(warehouse=warehouse, sequence=0))

    def next_zone_setting(self, now_zone_setting=None, reverse=False):
        '''
        get the next zone setting of the route after now zone setting,
        when reverse is True,return the previous zone setting of the route
        :param now_zone_setting: stock.RouteZoneSetting instance
        :param reverse: boolean
        :return: stock.RouteZoneSetting instance
        '''
        settings = self.route_zone_settings.all()
        if not reverse:
            if now_zone_setting:
                return settings.filter(sequence__gt=now_zone_setting.sequence).first()
            return settings.first()
        else:
            if now_zone_setting:
                return settings.filter(sequence__lt=now_zone_setting.sequence).order_by('-sequence').first()
            return settings.order_by('-sequence').first()


class RouteZoneSetting(models.Model):
    '''
    the setting of zone config the route's zone chain
    '''
    RELATED_NAME = 'route_zone_settings'

    name = models.CharField(
        _('name'),
        null=False,
        blank=False,
        max_length=60,
        help_text=_('the name of zone setting')
    )

    route = ActiveLimitForeignKey(
        'stock.Route',
        null=False,
        blank=False,
        verbose_name=_('route'),
        related_name=RELATED_NAME,
        help_text=_('the route of zone to chain together')
    )

    zone = ActiveLimitForeignKey(
        'stock.Zone',
        null=False,
        blank=False,
        verbose_name=_('zone'),
        related_name=RELATED_NAME,
        help_text=_('the zone that move must according to')
    )

    sequence = models.PositiveSmallIntegerField(
        _('sequence'),
        null=False,
        blank=False,
        default=0,
        help_text=_('the order of the zone in route')
    )

    @property
    def is_end(self):
        '''
        if this zone setting is the last in the chain of route
        :return: boolean
        '''
        return self.sequence == 32767

    def __str__(self):
        return '{}/{}/{}'.format(self.route, self.zone, self.sequence)

    class Meta:
        verbose_name = _('route zone setting')
        verbose_name_plural = _('route zone settings')
        unique_together = (
            ('route', 'sequence'),
            ('route', 'name')
        )
        ordering = ('sequence',)


class Procurement(BaseModel):
    '''
    procurement is the requirement of stock item from the location,
    it makes a series of move according to the route
    '''

    user = PartnerForeignKey(
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
        '''
        get the moves of doing status of this procurement
        :return:
        '''
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
        confirmed = Statement(inherits=active, state='confirmed')
        done = Statement(inherits=active, state='done')
        cancel = Statement(inherits=active, state='cancel')

    def confirm(self):
        '''
        change the procurement status from draft to confirmed
        :return: self
        '''
        self.check_to_set_state('draft', set_state='confirmed', raise_exception=True)
        return self

    def cancel(self):
        '''
        change the procurement status from draft or confirmed to cancel
        :return: self
        '''
        with transaction.atomic():
            self.check_to_set_state('draft', 'confirmed', set_state='cancel', raise_exception=True)
            for move in Move.get_state_queryset(
                    'cancel_able',
                    Move.objects.filter(procurement_detail__procurement=self)
            ):
                move.cancel()
            return self


class ProcurementDetail(models.Model, StateMachine):
    '''
    the detail of procurement config what item user want to move
    '''
    item = ActiveLimitForeignKey(
        'stock.Item',
        null=False,
        blank=False,
        verbose_name=_('item'),
        help_text=_('the item which will be move according to the route')
    )

    quantity = QuantityField(
        _('quantity'),
        null=False,
        blank=False,
        uom='product.template.uom',
        validators=[MinValueValidator(0)],
        help_text=_('the quantity of item will be move')
    )

    procurement = ActiveLimitForeignKey(
        'stock.Procurement',
        null=False,
        blank=False,
        verbose_name=_('procurement'),
        related_name='details',
        help_text=_('the procurement which detail belongs to')
    )

    route = ActiveLimitForeignKey(
        'stock.Route',
        null=False,
        blank=False,
        verbose_name=_('route'),
        related_name='details',
        help_text=_('the chain of zone config by route which item will move according to')
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
            Q(moves__isnull=True) &
            (Q(procurement__require_procurements__isnull=True) | Q(procurement__require_procurements__state='done'))
        )
        started = Statement(Q(moves__isnull=False))

    @property
    def doing_move(self):
        '''
        get all moves that which are create by this procurement detail
        :return: stock.Move instance
        '''
        return Move.get_state_queryset('doing').get(procurement_detail=self)

    def start(self, initial_location, end_location=None):
        '''
        when procurement status become confirmed,procurement detail can create
        the first move according to the route
        :param initial_location: stock.Location instance
        :param next_location: stock.Location instance
        :return: stock.Move instance
        '''
        with transaction.atomic():
            self.check_states('start_able', raise_exception=True)
            self.procurement.check_states('confirmed', raise_exception=True)
            next_zone_setting = self.route.route_zone_settings.all()[1]
            move = Move.objects.create(
                from_location=initial_location,
                to_location=end_location,
                procurement_detail=self,
                zone_setting=next_zone_setting,
                quantity=self.quantity,
                state='draft',
                is_return=False
            )
            move.confirm()
            return move


class Item(BaseModel):
    '''
    stock item is project what can be stock and move
    '''

    content_type = models.ForeignKey(
        ContentType,
        null=False,
        blank=False,
        verbose_name=_('content type'),
        related_name='item',
        help_text=_('the type of content reflect to the model')
    )

    object_id = models.PositiveIntegerField(
        _('item id'),
        null=False,
        blank=False,
        help_text=_('the primary key for the project')
    )

    instance = GenericForeignKey('content_type', 'object_id')

    @property
    def cache(self):
        if not hasattr(self,'__cache'):
            self.__cache = CacheItem(self)
        return self.__cache

    def __str__(self):
        return str(self.instance)

    class Meta:
        verbose_name = _('stock item')
        verbose_name_plural = _('stock items')
        unique_together = ('content_type', 'object_id')

    class States(BaseModel.States):
        active = BaseModel.States.active
        product = Statement(
            Q(content_type__app_label='product') & Q(content_type__model='product'),
            inherits=active
        )
        package_node = Statement(
            Q(content_type__app_label='stock') & Q(content_type__model='packagenode'),
            inherits=active
        )

    @property
    def item_name(self):
        '''
        get item key name
        :return: string
        '''
        return CacheItem.item_name(self)

    @property
    def item_lock_name(self):
        '''
        get item lock key name for zone
        :return: string
        '''
        return CacheItem.item_lock_name(self)
