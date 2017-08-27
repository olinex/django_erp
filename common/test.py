#!/usr/bin/env python3
#-*- coding:utf-8 -*-

import random
import string
from decimal import Decimal as D

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.test import TestCase
from apps.stock.models import (
    Warehouse, Location, Route, Procurement, ProcurementDetail,RouteZoneSetting
)

from apps.account.models import Province, City, Region, Address, Company
from apps.product.models import ProductCategory, ProductTemplate, UOM, Attribute, Lot

User=get_user_model()

class EnvSetUpTestCase(TestCase):

    def setUp(self):
        self.passwd = ''.join(random.sample(string.ascii_letters, 10))
        self.superuser = User.objects.create_superuser(
            username='testsuperuser',
            email='demosuperuser@163.com',
            password=self.passwd)
        self.normaluser = User.objects.create_user(
            username='testnormaluser',
            email='demouser@163.com',
            password=self.passwd)
        self.anonuser = AnonymousUser()
        self.superuser.profile.is_partner = True
        self.superuser.profile.save()
        self.province = Province.objects.create(
            country='China',
            name='province_test'
        )
        self.city = City.objects.create(
            province=self.province,
            name='city_test'
        )
        self.region = Region.objects.create(
            city=self.city,
            name='region_test'
        )
        self.address = Address.objects.create(
            region=self.region,
            name='address_test'
        )
        self.company = Company.objects.create(
            name='company_test',
            tel='13510440902'
        )
        self.category = ProductCategory.objects.create(
            name='category_test'
        )
        self.uom = UOM.objects.create(
            name='uom_test',
            symbol='uom',
            ratio=D('0.01'),
            category='m'
        )
        self.attr = Attribute.objects.create(
            name='attr_test',
            value=[1,2,3,4],
            extra_price=[1,2,3,4]
        )
        self.template = ProductTemplate.objects.create(
            name='template_test',
            stock_type='stock-no-expiration',
            uom=self.uom,
            category=self.category
        )
        self.template.attributes.add(self.attr)
        self.product = self.template.products.all()[0]
        self.product.salable = True
        self.product.purchasable = True
        self.product.rentable = True
        self.product.save()
        self.item = self.product.item
        self.lot = Lot.objects.create(
            name='lot_test',
            product=self.product
        )
        self.warehouse = Warehouse.objects.create(
            name='warehouse_test',
            user=self.superuser,
            address=self.address
        )
        self.zone_stock = self.warehouse.zones.get(usage='stock')
        self.zone_pick = self.warehouse.zones.get(usage='pick')
        self.zone_check = self.warehouse.zones.get(usage='check')
        self.zone_pack = self.warehouse.zones.get(usage='pack')
        self.zone_wait = self.warehouse.zones.get(usage='wait')
        self.zone_deliver = self.warehouse.zones.get(usage='deliver')
        self.zone_customer = self.warehouse.zones.get(usage='customer')
        self.zone_supplier = self.warehouse.zones.get(usage='supplier')
        self.zone_produce = self.warehouse.zones.get(usage='produce')
        self.zone_repair = self.warehouse.zones.get(usage='repair')
        self.zone_scrap = self.warehouse.zones.get(usage='scrap')
        self.zone_closeout = self.warehouse.zones.get(usage='closeout')
        self.zone_initial = self.warehouse.zones.get(usage='initial')
        self.zone_midway = self.warehouse.zones.get(usage='midway')
        self.location_stock = Location.objects.create(
            zone=self.zone_stock,
            is_virtual=False,
            x='0',y='0',z='0'
        )
        self.location_pick = Location.objects.create(
            zone=self.zone_pick,
            is_virtual=False,
            x='0',y='0',z='0'
        )
        self.location_pack = Location.objects.create(
            zone=self.zone_pack,
            is_virtual=False,
            x='0',y='0',z='0'
        )
        self.location_check = Location.objects.create(
            zone=self.zone_check,
            is_virtual=False,
            x='0',y='0',z='0'
        )
        self.location_wait = Location.objects.create(
            zone=self.zone_wait,
            is_virtual=False,
            x='0',y='0',z='0'
        )
        self.location_deliver = Location.objects.create(
            zone=self.zone_deliver,
            is_virtual=False,
            x='0',y='0',z='0'
        )
        self.location_customer = Location.objects.create(
            zone=self.zone_customer,
            is_virtual=False,
            x='0',y='0',z='0'
        )
        self.location_supplier = Location.objects.create(
            zone=self.zone_supplier,
            is_virtual=False,
            x='0',y='0',z='0'
        )
        self.location_produce = Location.objects.create(
            zone=self.zone_produce,
            is_virtual=False,
            x='0',y='0',z='0'
        )
        self.location_repair = Location.objects.create(
            zone=self.zone_repair,
            is_virtual=False,
            x='0',y='0',z='0'
        )
        self.location_scrap = self.zone_scrap.root_location
        self.location_closeout = self.zone_closeout.root_location
        self.location_initial = self.zone_initial.root_location
        self.location_midway = Location.objects.create(
            zone=self.zone_midway,
            is_virtual=False,
            x='0',y='0',z='0'
        )
        self.location_stock.change_parent_node(self.zone_stock.root_location)
        self.location_pick.change_parent_node(self.zone_pick.root_location)
        self.location_pack.change_parent_node(self.zone_pack.root_location)
        self.location_check.change_parent_node(self.zone_check.root_location)
        self.location_wait.change_parent_node(self.zone_wait.root_location)
        self.location_deliver.change_parent_node(self.zone_deliver.root_location)
        self.location_customer.change_parent_node(self.zone_customer.root_location)
        self.location_supplier.change_parent_node(self.zone_supplier.root_location)
        self.location_produce.change_parent_node(self.zone_produce.root_location)
        self.location_repair.change_parent_node(self.zone_repair.root_location)
        self.location_midway.change_parent_node(self.zone_midway.root_location)

        self.location_stock.cache.sync()
        self.location_pick.cache.sync()
        self.location_pack.cache.sync()
        self.location_check.cache.sync()
        self.location_wait.cache.sync()
        self.location_deliver.cache.sync()
        self.location_customer.cache.sync()
        self.location_supplier.cache.sync()
        self.location_produce.cache.sync()
        self.location_repair.cache.sync()
        self.location_scrap.cache.sync()
        self.location_closeout.cache.sync()
        self.location_initial.cache.sync()
        self.location_midway.cache.sync()

        self.product.item.cache.sync()

        self.route = Route.objects.create(
            name='route_test',
            warehouse=self.warehouse,
            route_type='produce-stock',
            sequence=1
        )
        RouteZoneSetting.objects.bulk_create([
            RouteZoneSetting(
                route=self.route,
                zone=getattr(self,zone),
                sequence=index + 1
            ) for index,zone in enumerate(['zone_pack','zone_check','zone_pick'])
        ])
        self.procurement = Procurement.objects.create(
            user=self.superuser
        )
        self.procurement_detail = ProcurementDetail.objects.create(
            item=self.item,
            procurement=self.procurement,
            quantity=D('5'),
            route=self.route
        )
        self.procurement.confirm()
        self.procurement_detail.start(self.location_produce,self.location_pack)
        self.move = self.procurement_detail.moves.first()



