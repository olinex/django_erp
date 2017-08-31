#!/usr/bin/env python3
#-*- coding:utf-8 -*-

from . import models
from decimal import Decimal as D
from common.tests import EnvSetUpTestCase
from common.exceptions import NotInStates

class ItemTestCase(EnvSetUpTestCase):

    def setUp(self):
        self.accountSetUp()
        self.productSetUp()
        self.stockSetUp()
        self.cls = models.Item

    def test_states(self):
        self.assertEqual(self.product.item.instance,self.product)
        self.assertTrue(self.product.item.check_states('active'))
        self.assertTrue(self.product.item.check_states('product'))
        self.assertFalse(self.product.item.check_states('package_node'))

    def test_get_quantity(self):
        cache = self.item.cache
        for usage in models.Zone.States.USAGE_STATES.keys():
            self.assertEqual(cache.get_quantity(usage,quantity_type='all'), 0)
            self.assertEqual(cache.get_quantity(usage,quantity_type='lock'), 0)
            self.assertEqual(cache.get_quantity(usage,quantity_type='now'), 0)
            cache.refresh(usage,1)
            self.assertEqual(cache.get_quantity(usage, quantity_type='all'), 1)
            self.assertEqual(cache.get_quantity(usage, quantity_type='lock'), 0)
            self.assertEqual(cache.get_quantity(usage, quantity_type='now'), 1)
            cache.refresh(usage, 1)
            self.assertEqual(cache.get_quantity(usage, quantity_type='all'), 2)
            self.assertEqual(cache.get_quantity(usage, quantity_type='lock'), 0)
            self.assertEqual(cache.get_quantity(usage, quantity_type='now'), 2)
            cache.lock(usage, 1)
            self.assertEqual(cache.get_quantity(usage, quantity_type='all'), 2)
            self.assertEqual(cache.get_quantity(usage, quantity_type='lock'), 1)
            self.assertEqual(cache.get_quantity(usage, quantity_type='now'), 1)
            cache.lock(usage, 1)
            self.assertEqual(cache.get_quantity(usage, quantity_type='all'), 2)
            self.assertEqual(cache.get_quantity(usage, quantity_type='lock'), 2)
            self.assertEqual(cache.get_quantity(usage, quantity_type='now'), 0)



class CacheLocationTestCase(EnvSetUpTestCase):

    def setUp(self):
        self.accountSetUp()
        self.productSetUp()
        self.stockSetUp()

    def test_fresh(self):
        for usage,explain in models.Zone.LAYOUT_USAGE:
            location = getattr(self,'location_{}'.format(usage))
            cache = location.cache
            cache.sync()
            cache.refresh(self.item,1)
            self.assertEqual(location.get_item_quantity(self.item),1)
            self.assertEqual(location.get_item_quantity(self.item,quantity_type='lock'), 0)
            cache.lock(self.item,1)
            self.assertEqual(location.get_item_quantity(self.item),0)
            self.assertEqual(location.get_item_quantity(self.item,quantity_type='lock'), 1)
            cache.lock(self.item,-1)
            self.assertEqual(location.get_item_quantity(self.item), 1)
            self.assertEqual(location.get_item_quantity(self.item,quantity_type='lock'), 0)
            cache.refresh(self.item,-1)
            self.assertEqual(location.get_item_quantity(self.item), 0)
            self.assertEqual(location.get_item_quantity(self.item,quantity_type='lock'), 0)
            cache.lock(self.item,5)
            self.assertEqual(location.get_item_quantity(self.item),-5)
            self.assertEqual(location.get_item_quantity(self.item,quantity_type='lock'), 5)
            cache.refresh(self.item,1)
            self.assertEqual(location.get_item_quantity(self.item),-4)
            self.assertEqual(location.get_item_quantity(self.item,quantity_type='lock'), 5)
            cache.free_all(self.item)
            self.assertEqual(location.get_item_quantity(self.item), 1)
            self.assertEqual(location.get_item_quantity(self.item,quantity_type='lock'), 0)



class RouteTestCase(EnvSetUpTestCase):

    def setUp(self):
        self.accountSetUp()
        self.productSetUp()
        self.stockSetUp()
        self.cls = models.Route

    def test_get_default_route(self):
        for route_type in self.cls.ROUTE_TYPE:
            route = self.cls.get_default_route(self.warehouse,route_type[0])
            self.assertEqual(route.length,2)
            self.assertEqual(route.initial_zone,route.initial_setting.zone)
            self.assertEqual(route.end_zone,route.end_setting.zone)
            self.assertEqual(route.initial_zone,getattr(self,'zone_{}'.format(route.route_type.split('_')[0])))
            self.assertEqual(route.end_zone,getattr(self,'zone_{}'.format(route.route_type.split('_')[1])))

    def test_next_zone_setting(self):
        now_zone_setting = None
        next_zone_setting = self.route.next_zone_setting(now_zone_setting=now_zone_setting)
        previous_zone_setting = self.route.next_zone_setting(now_zone_setting=now_zone_setting, reverse=True)
        self.assertEqual(next_zone_setting.zone, self.zone_produce)
        self.assertEqual(previous_zone_setting.zone, self.zone_stock)
        # now is produce zone
        now_zone_setting = self.route.next_zone_setting(now_zone_setting=now_zone_setting)
        next_zone_setting = self.route.next_zone_setting(now_zone_setting=now_zone_setting)
        previous_zone_setting = self.route.next_zone_setting(now_zone_setting=now_zone_setting,reverse=True)
        self.assertEqual(next_zone_setting.zone,self.zone_pack)
        self.assertIsNone(previous_zone_setting)
        # now is pack zone
        now_zone_setting = self.route.next_zone_setting(now_zone_setting=now_zone_setting)
        next_zone_setting = self.route.next_zone_setting(now_zone_setting=now_zone_setting)
        previous_zone_setting = self.route.next_zone_setting(now_zone_setting=now_zone_setting, reverse=True)
        self.assertEqual(next_zone_setting.zone, self.zone_check)
        self.assertEqual(previous_zone_setting.zone, self.zone_produce)
        # now is check zone
        now_zone_setting = self.route.next_zone_setting(now_zone_setting=now_zone_setting)
        next_zone_setting = self.route.next_zone_setting(now_zone_setting=now_zone_setting)
        previous_zone_setting = self.route.next_zone_setting(now_zone_setting=now_zone_setting, reverse=True)
        self.assertEqual(next_zone_setting.zone, self.zone_wait)
        self.assertEqual(previous_zone_setting.zone, self.zone_pack)
        # now is wait zone
        now_zone_setting = self.route.next_zone_setting(now_zone_setting=now_zone_setting)
        next_zone_setting = self.route.next_zone_setting(now_zone_setting=now_zone_setting)
        previous_zone_setting = self.route.next_zone_setting(now_zone_setting=now_zone_setting, reverse=True)
        self.assertEqual(next_zone_setting.zone, self.zone_stock)
        self.assertEqual(previous_zone_setting.zone, self.zone_check)
        # now is stock zone
        now_zone_setting = self.route.next_zone_setting(now_zone_setting=now_zone_setting)
        next_zone_setting = self.route.next_zone_setting(now_zone_setting=now_zone_setting)
        previous_zone_setting = self.route.next_zone_setting(now_zone_setting=now_zone_setting, reverse=True)
        self.assertIsNone(next_zone_setting)
        self.assertEqual(previous_zone_setting.zone, self.zone_wait)


class CacheItemTestCase(EnvSetUpTestCase):

    def setUp(self):
        self.accountSetUp()
        self.productSetUp()
        self.stockSetUp()
        self.item.cache.sync()

    def test_refresh(self):
        cache = self.item.cache
        self.assertEqual(cache.all(),0)
        self.assertEqual(cache.settled(),0)
        self.assertEqual(cache.transporting(),0)
        self.assertEqual(cache.scrap(),0)
        self.assertEqual(cache.closeout(),0)

        for usage in models.Zone.LAYOUT_USAGE:
            self.assertEqual(cache.refresh(usage[0], 1),1)
            self.assertEqual(cache.get_quantity(usage[0]),1)
            self.assertEqual(cache.refresh(usage[0], -1),0)
            self.assertEqual(cache.get_quantity(usage[0]), 0)


class LocationTestCase(EnvSetUpTestCase):


    def setUp(self):
        self.accountSetUp()
        self.productSetUp()
        self.stockSetUp()

    def test_location_tree(self):
        self.assertTrue(self.location_stock.all_parent_nodes)
        self.assertFalse(self.location_stock.all_child_nodes)
        self.assertEqual(self.location_stock.root_node,self.zone_stock.root_location)
        self.assertEqual(self.location_stock.all_parent_nodes.first(),self.zone_stock.root_location)
        self.assertEqual(self.zone_stock.root_location.all_child_nodes.first(),self.location_stock)
        self.assertFalse(self.location_stock.sibling_nodes)

class PackOrderTestCase(EnvSetUpTestCase):

    def setUp(self):
        self.accountSetUp()
        self.productSetUp()
        self.stockSetUp()
        self.pack_order = models.PackOrder.objects.create(
            is_pack=True,
            create_user=self.super_user,
            location=self.location_pack
        )
        self.pack_order_line = models.PackOrderLine.objects.create(
            order=self.pack_order,
            package_node=self.package_node,
            quantity=1
        )

    def test_confirm_to_done(self):
        self.assertTrue(self.pack_order.check_states('draft'))
        self.assertFalse(self.pack_order.check_states('confirmed'))
        self.assertFalse(self.pack_order.check_states('done'))
        for product in self.template.products.all():
            self.assertEqual(self.location_pack.get_item_quantity(product.item), 0)
            self.assertEqual(self.location_closeout.get_item_quantity(product.item), 0)
        self.assertEqual(self.location_pack.get_item_quantity(self.package_node.item), 0)
        self.assertEqual(self.location_closeout.get_item_quantity(self.package_node.item), 0)
        self.assertEqual(self.pack_order.state,'draft')

        self.assertEqual(self.pack_order.confirm(),self.pack_order)
        self.assertFalse(self.pack_order.check_states('draft'))
        self.assertTrue(self.pack_order.check_states('confirmed'))
        self.assertFalse(self.pack_order.check_states('done'))
        for product in self.template.products.all():
            self.assertEqual(self.location_pack.get_item_quantity(product.item), 0)
            self.assertEqual(self.location_closeout.get_item_quantity(product.item), 0)
        self.assertEqual(self.location_pack.get_item_quantity(self.package_node.item), 0)
        self.assertEqual(self.location_closeout.get_item_quantity(self.package_node.item), 0)
        self.assertTrue(self.pack_order.procurement.check_states('confirmed'))

        self.assertEqual(self.pack_order_line.done(), self.pack_order_line)
        self.assertFalse(self.pack_order.check_states('draft'))
        self.assertFalse(self.pack_order.check_states('confirmed'))
        self.assertTrue(self.pack_order.check_states('done'))
        for product in self.template.products.all():
            self.assertEqual(self.location_pack.get_item_quantity(product.item), -9)
            self.assertEqual(self.location_closeout.get_item_quantity(product.item), 9)
        self.assertEqual(self.location_pack.get_item_quantity(self.package_node.item), 1)
        self.assertEqual(self.location_closeout.get_item_quantity(self.package_node.item), -1)
        self.assertTrue(self.pack_order.procurement.check_states('done'))


class WarehouseTestCase(EnvSetUpTestCase):

    def setUp(self):
        self.accountSetUp()
        self.productSetUp()
        self.stockSetUp()
        self.procurement = models.Procurement.objects.create(user=self.super_user)
        self.procurement_detail = models.ProcurementDetail.objects.create(
            item=self.item,
            procurement=self.procurement,
            quantity=D('5'),
            route=self.route
        )
        self.procurement.confirm()
        self.procurement_detail.start(self.location_produce)
        self.move = self.procurement_detail.moves.first()

    def test_get_default_location(self):
        for usage in models.Zone.INDIVISIBLE_USAGE:
            self.assertEqual(self.warehouse.get_default_location(usage).zone.usage,usage)

    def test_move_transfer(self):
        self.move.to_location=self.location_pack
        self.move.save()
        print(self.move)
        # at produce lock 5
        self.assertEqual(self.location_produce.get_item_quantity(self.item),D('-5'))
        self.assertEqual(self.location_pack.get_item_quantity(self.item),D('0'))
        self.assertEqual(self.location_check.get_item_quantity(self.item),D('0'))
        self.assertEqual(self.location_wait.get_item_quantity(self.item), D('0'))
        self.assertEqual(self.location_stock.get_item_quantity(self.item), D('0'))
        self.assertEqual(self.item.cache.all(),D('0'))
        self.assertEqual(self.item.cache.settled(),D('0'))
        self.assertEqual(self.item.cache.transporting(),D('0'))
        self.assertEqual(self.move.done(),self.move)
        # at pack lock 0
        self.assertFalse(self.procurement.check_states('done'))
        with self.assertRaises(NotInStates):
            self.move.done()

        self.next_move = self.move.to_move
        self.next_move.to_location = self.location_check
        self.next_move.save()
        print(self.next_move)
        # at pack lock 5
        self.assertEqual(self.location_produce.get_item_quantity(self.item), D('-5'))
        self.assertEqual(self.location_pack.get_item_quantity(self.item), D('0'))
        self.assertEqual(self.location_check.get_item_quantity(self.item), D('0'))
        self.assertEqual(self.location_wait.get_item_quantity(self.item), D('0'))
        self.assertEqual(self.location_stock.get_item_quantity(self.item), D('0'))
        self.assertEqual(self.item.cache.all(), D('5'))
        self.assertEqual(self.item.cache.settled(), D('0'))
        self.assertEqual(self.item.cache.transporting(), D('5'))
        self.assertEqual(self.next_move.done(),self.next_move)
        # at check lock 0
        self.assertFalse(self.procurement.check_states('done'))
        with self.assertRaises(NotInStates):
            self.next_move.done()

        self.next_move = self.next_move.to_move
        self.next_move.to_location = self.location_wait
        self.next_move.save()
        print(self.next_move)
        # at check lock 5
        self.assertEqual(self.location_produce.get_item_quantity(self.item), D('-5'))
        self.assertEqual(self.location_pack.get_item_quantity(self.item), D('0'))
        self.assertEqual(self.location_check.get_item_quantity(self.item), D('0'))
        self.assertEqual(self.location_wait.get_item_quantity(self.item), D('0'))
        self.assertEqual(self.location_stock.get_item_quantity(self.item), D('0'))
        self.assertEqual(self.item.cache.all(), D('5'))
        self.assertEqual(self.item.cache.settled(), D('0'))
        self.assertEqual(self.item.cache.transporting(), D('5'))
        self.assertEqual(self.next_move.done(),self.next_move)
        # at pick lock 0
        self.assertFalse(self.procurement.check_states('done'))
        with self.assertRaises(NotInStates):
            self.next_move.done()

        self.next_move = self.next_move.to_move
        self.next_move.to_location = self.location_stock
        self.next_move.save()
        print(self.next_move)
        # at pick lock 5
        self.assertEqual(self.location_produce.get_item_quantity(self.item), D('-5'))
        self.assertEqual(self.location_pack.get_item_quantity(self.item), D('0'))
        self.assertEqual(self.location_check.get_item_quantity(self.item), D('0'))
        self.assertEqual(self.location_wait.get_item_quantity(self.item), D('0'))
        self.assertEqual(self.location_stock.get_item_quantity(self.item), D('0'))
        self.assertEqual(self.item.cache.all(), D('5'))
        self.assertEqual(self.item.cache.settled(), D('0'))
        self.assertEqual(self.item.cache.transporting(), D('5'))

        self.assertEqual(self.procurement.cancel(),self.procurement)
        self.assertEqual(self.next_move.done(),self.next_move)
        # at stock lock 0
        self.assertFalse(self.procurement.check_states('done'))
        self.assertTrue(self.procurement.check_states('cancel'))
        with self.assertRaises(NotInStates):
            self.next_move.done()

        self.next_move = self.next_move.to_move
        self.next_move.to_location = self.location_wait
        self.next_move.save()
        print(self.next_move)
        # at stock lock 5
        self.assertEqual(self.location_produce.get_item_quantity(self.item), D('-5'))
        self.assertEqual(self.location_pack.get_item_quantity(self.item), D('0'))
        self.assertEqual(self.location_check.get_item_quantity(self.item), D('0'))
        self.assertEqual(self.location_wait.get_item_quantity(self.item), D('0'))
        self.assertEqual(self.location_stock.get_item_quantity(self.item), D('0'))
        self.assertEqual(self.item.cache.all(), D('5'))
        self.assertEqual(self.item.cache.settled(), D('0'))
        self.assertEqual(self.item.cache.transporting(), D('0'))
        self.assertEqual(self.next_move.done(),self.next_move)
        # at pick lock 0
        self.assertTrue(self.procurement.check_states('cancel'))
        with self.assertRaises(NotInStates):
            self.next_move.done()

        self.next_move = self.next_move.to_move
        self.next_move.to_location = self.location_check
        self.next_move.save()
        print(self.next_move)
        # at pick lock 5
        self.assertEqual(self.location_produce.get_item_quantity(self.item), D('-5'))
        self.assertEqual(self.location_pack.get_item_quantity(self.item), D('0'))
        self.assertEqual(self.location_check.get_item_quantity(self.item), D('0'))
        self.assertEqual(self.location_wait.get_item_quantity(self.item), D('0'))
        self.assertEqual(self.location_stock.get_item_quantity(self.item), D('0'))
        self.assertEqual(self.item.cache.all(), D('5'))
        self.assertEqual(self.item.cache.settled(), D('0'))
        self.assertEqual(self.item.cache.transporting(), D('5'))
        self.assertEqual(self.next_move.done(),self.next_move)
        # at check lock 0
        self.assertTrue(self.procurement.check_states('cancel'))
        with self.assertRaises(NotInStates):
            self.next_move.done()

        self.next_move = self.next_move.to_move
        self.next_move.to_location = self.location_pack
        self.next_move.save()
        print(self.next_move)
        # at check lock 5
        self.assertEqual(self.location_produce.get_item_quantity(self.item), D('-5'))
        self.assertEqual(self.location_pack.get_item_quantity(self.item), D('0'))
        self.assertEqual(self.location_check.get_item_quantity(self.item), D('0'))
        self.assertEqual(self.location_wait.get_item_quantity(self.item), D('0'))
        self.assertEqual(self.location_stock.get_item_quantity(self.item), D('0'))
        self.assertEqual(self.item.cache.all(), D('5'))
        self.assertEqual(self.item.cache.settled(), D('0'))
        self.assertEqual(self.item.cache.transporting(), D('5'))
        self.assertEqual(self.next_move.done(),self.next_move)
        # at pack lock 0
        self.assertTrue(self.procurement.check_states('cancel'))
        with self.assertRaises(NotInStates):
            self.next_move.done()

        self.next_move = self.next_move.to_move
        self.next_move.to_location = self.location_produce
        self.next_move.save()
        print(self.next_move)
        # at pack lock 5
        self.assertEqual(self.location_produce.get_item_quantity(self.item), D('-5'))
        self.assertEqual(self.location_pack.get_item_quantity(self.item), D('0'))
        self.assertEqual(self.location_check.get_item_quantity(self.item), D('0'))
        self.assertEqual(self.location_wait.get_item_quantity(self.item), D('0'))
        self.assertEqual(self.location_stock.get_item_quantity(self.item), D('0'))
        self.assertEqual(self.item.cache.all(), D('5'))
        self.assertEqual(self.item.cache.settled(), D('0'))
        self.assertEqual(self.item.cache.transporting(), D('5'))
        self.assertEqual(self.next_move.done(),self.next_move)
        # at produce lock 0
        self.assertTrue(self.procurement.check_states('cancel'))
        with self.assertRaises(NotInStates):
            self.next_move.done()

        self.assertEqual(self.location_produce.get_item_quantity(self.item), D('0'))
        self.assertEqual(self.location_pack.get_item_quantity(self.item), D('0'))
        self.assertEqual(self.location_check.get_item_quantity(self.item), D('0'))
        self.assertEqual(self.location_wait.get_item_quantity(self.item), D('0'))
        self.assertEqual(self.location_stock.get_item_quantity(self.item), D('0'))
        self.assertEqual(self.item.cache.all(), D('0'))
        self.assertEqual(self.item.cache.settled(), D('0'))
        self.assertEqual(self.item.cache.transporting(), D('0'))