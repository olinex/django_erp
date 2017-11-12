#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
@author:    olinex
@time:      2017/8/29 上午12:52
"""

import random
import string
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.test import TestCase
from django_base.models import Province, City, Region, Address

User = get_user_model()


class EnvSetUpTestCase(TestCase):
    def accountSetUp(self):
        self.password = ''.join(random.sample(string.ascii_letters, 10))
        self.super_user = User.objects.create_superuser(
            username='test_super_user',
            email='demosuperuser@163.com',
            password=self.password)
        self.normal_user = User.objects.create_user(
            username='test_normal_user',
            email='demouser@163.com',
            password=self.password)
        self.anon_user = AnonymousUser()
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
        self.partner = Partner.objects.create(
            name='partner_test',
            phone='12342342342'
        )

    # def productSetUp(self):
    #     self.category = ProductCategory.objects.create(
    #         name='category_test'
    #     )
    #     self.uom = UOM.objects.create(
    #         name='uom_test',
    #         symbol='uom',
    #         ratio=D('0.01'),
    #         category='m'
    #     )
    #     self.attr = Attribute.objects.create(
    #         name='attr_test',
    #         value=[1, 2, 3, 4],
    #         extra_price=[1, 2, 3, 4]
    #     )
    #     self.template = ProductTemplate.objects.create(
    #         name='template_test',
    #         stock_type='stock-no-expiration',
    #         uom=self.uom,
    #         category=self.category
    #     )
    #     self.template.attributes.add(self.attr)
    #     self.product = self.template.product_set.first()
    #     self.item = self.product.item
    #     self.item.__class__ = Item
    #     self.lot = Lot.objects.create(
    #         name='lot_test',
    #         product=self.product
    #     )
    #     self.package_type = PackageType.objects.create(
    #         name='package_type_test'
    #     )
    #     PackageTypeSetting.objects.bulk_create([
    #         PackageTypeSetting(
    #             package_type=self.package_type,
    #             item=product.item,
    #             max_quantity=10
    #         ) for product in self.template.product_set.all()
    #     ])
    #     self.package_template = PackageTemplate.objects.create(
    #         name='package_template_test',
    #         package_type=self.package_type
    #     )
    #     PackageTemplateSetting.objects.bulk_create([
    #         PackageTemplateSetting(
    #             package_template=self.package_template,
    #             type_setting=setting,
    #             quantity=9
    #         ) for setting in self.package_type.packagetypesetting_set.all()
    #     ])
    #     self.package_node = PackageNode.objects.create(
    #         template=self.package_template,
    #         quantity=1
    #     )
    #
    # def stockSetUp(self):
    #     self.warehouse = Warehouse.objects.create(
    #         name='warehouse_1',
    #         manager=self.super_user,
    #         address=self.address
    #     )
    #     self.location_root = self.warehouse.root_location
    #     self.location_stock = Location.objects.create(
    #         warehouse=self.warehouse,
    #         zone='stock',
    #         is_virtual=False,
    #         x='0', y='0', z='0'
    #     )
    #     self.location_pack = Location.objects.create(
    #         warehouse=self.warehouse,
    #         zone='pack',
    #         is_virtual=False,
    #         x='0', y='0', z='0'
    #     )
    #     self.location_check = Location.objects.create(
    #         warehouse=self.warehouse,
    #         zone='check',
    #         is_virtual=False,
    #         x='0', y='0', z='0'
    #     )
    #     self.location_wait = Location.objects.create(
    #         warehouse=self.warehouse,
    #         zone='wait',
    #         is_virtual=False,
    #         x='0', y='0', z='0'
    #     )
    #     self.location_deliver = Location.objects.create(
    #         warehouse=self.warehouse,
    #         zone='deliver',
    #         is_virtual=False,
    #         x='0', y='0', z='0'
    #     )
    #     self.location_customer = Location.objects.create(
    #         warehouse=self.warehouse,
    #         zone='customer',
    #         is_virtual=False,
    #         x='0', y='0', z='0'
    #     )
    #     self.location_supplier = Location.objects.create(
    #         warehouse=self.warehouse,
    #         zone='supplier',
    #         is_virtual=False,
    #         x='0', y='0', z='0'
    #     )
    #     self.location_produce = Location.objects.create(
    #         warehouse=self.warehouse,
    #         zone='produce',
    #         is_virtual=False,
    #         x='0', y='0', z='0'
    #     )
    #     self.location_repair = Location.objects.create(
    #         warehouse=self.warehouse,
    #         zone='repair',
    #         is_virtual=False,
    #         x='0', y='0', z='0'
    #     )
    #     self.location_scrap = Location.objects.create(
    #         warehouse=self.warehouse,
    #         zone='scrap',
    #         is_virtual=False,
    #         x='0', y='0', z='0'
    #     )
    #     self.location_closeout = self.warehouse.closeout_location
    #     self.location_initial = self.warehouse.initial_location
    #
    #     self.location_stock.change_parent_node(self.warehouse.get_root_location('stock'))
    #     self.location_pack.change_parent_node(self.warehouse.get_root_location('pack'))
    #     self.location_check.change_parent_node(self.warehouse.get_root_location('check'))
    #     self.location_wait.change_parent_node(self.warehouse.get_root_location('wait'))
    #     self.location_deliver.change_parent_node(self.warehouse.get_root_location('deliver'))
    #     self.location_customer.change_parent_node(self.warehouse.get_root_location('customer'))
    #     self.location_supplier.change_parent_node(self.warehouse.get_root_location('supplier'))
    #     self.location_produce.change_parent_node(self.warehouse.get_root_location('produce'))
    #     self.location_repair.change_parent_node(self.warehouse.get_root_location('repair'))
    #     self.location_scrap.change_parent_node(self.warehouse.get_root_location('scrap'))
    #
    #     self.location_stock.cache.sync()
    #     self.location_pack.cache.sync()
    #     self.location_check.cache.sync()
    #     self.location_wait.cache.sync()
    #     self.location_deliver.cache.sync()
    #     self.location_customer.cache.sync()
    #     self.location_supplier.cache.sync()
    #     self.location_produce.cache.sync()
    #     self.location_repair.cache.sync()
    #     self.location_scrap.cache.sync()
    #     self.location_closeout.cache.sync()
    #     self.location_initial.cache.sync()
    #
    #     self.item.cache.sync()
    #
    #     self.route = Route.objects.create(
    #         name='route_test',
    #         warehouse=self.warehouse,
    #         sequence=1
    #     )
    #     RouteSetting.objects.bulk_create([
    #         RouteSetting(
    #             name=str(index),
    #             route=self.route,
    #             location=getattr(self, location),
    #             sequence=index + 1
    #         ) for index, location in enumerate(['location_pack', 'location_check', 'location_wait'])
    #     ])
    #     RouteSetting.objects.create(name='initial', route=self.route, location=self.location_produce, sequence=0)
    #     RouteSetting.objects.create(name='end', route=self.route, location=self.location_stock, sequence=10)
