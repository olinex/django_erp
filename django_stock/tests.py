#!/usr/bin/env python3
# -*- coding:utf-8 -*-

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
        self.assertEqual(self.product.item.instance, self.product)
        self.assertTrue(self.product.item.check_states('active'))
        self.assertTrue(self.product.item.check_states('product'))
        self.assertFalse(self.product.item.check_states('package_node'))

    def test_get_quantity(self):
        cache = self.item.cache
        for zone in models.Location.States.ZONE_STATES.keys():
            self.assertEqual(cache.get_quantity(zone, quantity_type='all'), 0)
            self.assertEqual(cache.get_quantity(zone, quantity_type='lock'), 0)
            self.assertEqual(cache.get_quantity(zone, quantity_type='now'), 0)
            cache.refresh(zone, 1)
            self.assertEqual(cache.get_quantity(zone, quantity_type='all'), 1)
            self.assertEqual(cache.get_quantity(zone, quantity_type='lock'), 0)
            self.assertEqual(cache.get_quantity(zone, quantity_type='now'), 1)
            cache.refresh(zone, 1)
            self.assertEqual(cache.get_quantity(zone, quantity_type='all'), 2)
            self.assertEqual(cache.get_quantity(zone, quantity_type='lock'), 0)
            self.assertEqual(cache.get_quantity(zone, quantity_type='now'), 2)
            cache.lock(zone, 1)
            self.assertEqual(cache.get_quantity(zone, quantity_type='all'), 2)
            self.assertEqual(cache.get_quantity(zone, quantity_type='lock'), 1)
            self.assertEqual(cache.get_quantity(zone, quantity_type='now'), 1)
            cache.lock(zone, 1)
            self.assertEqual(cache.get_quantity(zone, quantity_type='all'), 2)
            self.assertEqual(cache.get_quantity(zone, quantity_type='lock'), 2)
            self.assertEqual(cache.get_quantity(zone, quantity_type='now'), 0)


class CacheLocationTestCase(EnvSetUpTestCase):
    def setUp(self):
        self.accountSetUp()
        self.productSetUp()
        self.stockSetUp()

    def test_fresh(self):
        for usage, explain in models.Location.ZONE:
            if usage != 'root':
                location = getattr(self, 'location_{}'.format(usage))
                cache = location.cache
                cache.sync()
                cache.refresh(self.item, 1)
                self.assertEqual(location.get_item_quantity(self.item), 1)
                self.assertEqual(location.get_item_quantity(self.item, quantity_type='lock'), 0)
                cache.lock(self.item, 1)
                self.assertEqual(location.get_item_quantity(self.item), 0)
                self.assertEqual(location.get_item_quantity(self.item, quantity_type='lock'), 1)
                cache.lock(self.item, -1)
                self.assertEqual(location.get_item_quantity(self.item), 1)
                self.assertEqual(location.get_item_quantity(self.item, quantity_type='lock'), 0)
                cache.refresh(self.item, -1)
                self.assertEqual(location.get_item_quantity(self.item), 0)
                self.assertEqual(location.get_item_quantity(self.item, quantity_type='lock'), 0)
                cache.lock(self.item, 5)
                self.assertEqual(location.get_item_quantity(self.item), -5)
                self.assertEqual(location.get_item_quantity(self.item, quantity_type='lock'), 5)
                cache.refresh(self.item, 1)
                self.assertEqual(location.get_item_quantity(self.item), -4)
                self.assertEqual(location.get_item_quantity(self.item, quantity_type='lock'), 5)
                cache.free_all(self.item)
                self.assertEqual(location.get_item_quantity(self.item), 1)
                self.assertEqual(location.get_item_quantity(self.item, quantity_type='lock'), 0)


class RouteTestCase(EnvSetUpTestCase):
    def setUp(self):
        self.accountSetUp()
        self.productSetUp()
        self.stockSetUp()
        self.cls = models.Route

    def test_get_default_route(self):
        for route_type in self.cls.ROUTE_TYPE:
            route = self.cls.get_default_route(self.warehouse, route_type[0])
            self.assertEqual(route.length, 2)
            self.assertEqual(route.warehouse, route.initial_setting.location.warehouse)
            self.assertEqual(route.warehouse, route.end_setting.location.warehouse)
            self.assertEqual(route.initial_setting.location.zone, route_type[0].split('_')[0])
            self.assertEqual(route.end_setting.location.zone, route_type[0].split('_')[1])

    def test_next_route_setting(self):
        now_route_setting = None
        next_route_setting = self.route.next_route_setting(now_route_setting=now_route_setting)
        previous_route_setting = self.route.next_route_setting(now_route_setting=now_route_setting, reverse=True)
        self.assertEqual(next_route_setting.location.zone, 'produce')
        self.assertEqual(previous_route_setting.location.zone, 'stock')
        # now is produce zone
        now_route_setting = self.route.next_route_setting(now_route_setting=now_route_setting)
        next_route_setting = self.route.next_route_setting(now_route_setting=now_route_setting)
        previous_route_setting = self.route.next_route_setting(now_route_setting=now_route_setting, reverse=True)
        self.assertEqual(next_route_setting.location.zone, 'pack')
        self.assertIsNone(previous_route_setting)
        # now is pack zone
        now_route_setting = self.route.next_route_setting(now_route_setting=now_route_setting)
        next_route_setting = self.route.next_route_setting(now_route_setting=now_route_setting)
        previous_route_setting = self.route.next_route_setting(now_route_setting=now_route_setting, reverse=True)
        self.assertEqual(next_route_setting.location.zone, 'check')
        self.assertEqual(previous_route_setting.location.zone, 'produce')
        # now is check zone
        now_route_setting = self.route.next_route_setting(now_route_setting=now_route_setting)
        next_route_setting = self.route.next_route_setting(now_route_setting=now_route_setting)
        previous_route_setting = self.route.next_route_setting(now_route_setting=now_route_setting, reverse=True)
        self.assertEqual(next_route_setting.location.zone, 'wait')
        self.assertEqual(previous_route_setting.location.zone, 'pack')
        # now is wait zone
        now_route_setting = self.route.next_route_setting(now_route_setting=now_route_setting)
        next_route_setting = self.route.next_route_setting(now_route_setting=now_route_setting)
        previous_route_setting = self.route.next_route_setting(now_route_setting=now_route_setting, reverse=True)
        self.assertEqual(next_route_setting.location.zone, 'stock')
        self.assertEqual(previous_route_setting.location.zone, 'check')
        # now is stock zone
        now_route_setting = self.route.next_route_setting(now_route_setting=now_route_setting)
        next_route_setting = self.route.next_route_setting(now_route_setting=now_route_setting)
        previous_route_setting = self.route.next_route_setting(now_route_setting=now_route_setting, reverse=True)
        self.assertIsNone(next_route_setting)
        self.assertEqual(previous_route_setting.location.zone, 'wait')


class CacheItemTestCase(EnvSetUpTestCase):
    def setUp(self):
        self.accountSetUp()
        self.productSetUp()
        self.stockSetUp()
        self.item.cache.sync()

    def test_refresh(self):
        cache = self.item.cache
        self.assertEqual(cache.all(), 0)
        self.assertEqual(cache.settled(), 0)
        self.assertEqual(cache.transporting(), 0)
        self.assertEqual(cache.scrap(), 0)
        self.assertEqual(cache.closeout(), 0)

        for zone in models.Location.ZONE:
            self.assertEqual(cache.refresh(zone[0], 1), 1)
            self.assertEqual(cache.get_quantity(zone[0]), 1)
            self.assertEqual(cache.refresh(zone[0], -1), 0)
            self.assertEqual(cache.get_quantity(zone[0]), 0)


class LocationTestCase(EnvSetUpTestCase):
    def setUp(self):
        self.accountSetUp()
        self.productSetUp()
        self.stockSetUp()

    def test_location_tree(self):
        self.assertTrue(self.location_stock.all_parent_nodes)
        self.assertFalse(self.location_stock.all_child_nodes)
        self.assertEqual(self.location_stock.root_node.zone, 'root')
        self.assertTrue(self.warehouse.root_location in self.location_stock.all_parent_nodes)
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
        for product in self.template.product_set.all():
            self.assertEqual(self.location_pack.get_item_quantity(product.item), 0)
            self.assertEqual(self.location_closeout.get_item_quantity(product.item), 0)
        self.assertEqual(self.location_pack.get_item_quantity(self.package_node.item), 0)
        self.assertEqual(self.location_closeout.get_item_quantity(self.package_node.item), 0)
        self.assertEqual(self.pack_order.state, 'draft')

        self.assertEqual(self.pack_order.confirm(), self.pack_order)
        self.assertFalse(self.pack_order.check_states('draft'))
        self.assertTrue(self.pack_order.check_states('confirmed'))
        self.assertFalse(self.pack_order.check_states('done'))
        for product in self.template.product_set.all():
            self.assertEqual(self.location_pack.get_item_quantity(product.item), 0)
            self.assertEqual(self.location_closeout.get_item_quantity(product.item), 0)
        self.assertEqual(self.location_pack.get_item_quantity(self.package_node.item), 0)
        self.assertEqual(self.location_closeout.get_item_quantity(self.package_node.item), 0)
        self.assertTrue(self.pack_order.procurement.check_states('confirmed'))

        self.assertEqual(self.pack_order_line.done(), self.pack_order_line)
        self.assertFalse(self.pack_order.check_states('draft'))
        self.assertFalse(self.pack_order.check_states('confirmed'))
        self.assertTrue(self.pack_order.check_states('done'))
        for product in self.template.product_set.all():
            self.assertEqual(self.location_pack.get_item_quantity(product.item), -9)
            self.assertEqual(self.location_closeout.get_item_quantity(product.item), 9)
        self.assertEqual(self.location_pack.get_item_quantity(self.package_node.item), 1)
        self.assertEqual(self.location_closeout.get_item_quantity(self.package_node.item), -1)
        self.assertTrue(self.pack_order.procurement.check_states('done'))


class ScrapOrderTestCase(EnvSetUpTestCase):
    def setUp(self):
        self.accountSetUp()
        self.productSetUp()
        self.stockSetUp()
        self.scrap_order_produce = models.ScrapOrder.objects.create(
            location=self.location_produce,
            create_user=self.super_user

        )
        models.ScrapOrderLine.objects.create(
            order=self.scrap_order_produce,
            item=self.item,
            quantity=1
        )
        self.scrap_order_stock = models.ScrapOrder.objects.create(
            location=self.location_stock,
            create_user=self.super_user
        )
        models.ScrapOrderLine.objects.create(
            order=self.scrap_order_stock,
            item=self.item,
            quantity=1
        )
        self.scrap_order_pack = models.ScrapOrder.objects.create(
            location=self.location_pack,
            create_user=self.super_user

        )
        models.ScrapOrderLine.objects.create(
            order=self.scrap_order_pack,
            item=self.item,
            quantity=1
        )
        self.scrap_order_repair = models.ScrapOrder.objects.create(
            location=self.location_repair,
            create_user=self.super_user

        )
        models.ScrapOrderLine.objects.create(
            order=self.scrap_order_repair,
            item=self.item,
            quantity=1
        )
        self.scrap_order_check = models.ScrapOrder.objects.create(
            location=self.location_check,
            create_user=self.super_user

        )
        models.ScrapOrderLine.objects.create(
            order=self.scrap_order_check,
            item=self.item,
            quantity=1
        )

    def test_produce_confirm_to_done(self):
        self.assertTrue(self.scrap_order_produce.check_states('draft'))
        self.assertFalse(self.scrap_order_produce.check_states('confirmed'))
        self.assertFalse(self.scrap_order_produce.check_states('done'))
        self.assertEqual(self.location_scrap.get_item_quantity(self.item), 0)
        self.assertEqual(self.location_produce.get_item_quantity(self.item), 0)
        self.assertEqual(self.scrap_order_produce.state, 'draft')

        self.assertEqual(self.scrap_order_produce.confirm(), self.scrap_order_produce)
        self.scrap_produce_move = self.scrap_order_produce.scraporderline_set.first().detail.doing_move
        self.assertFalse(self.scrap_order_produce.check_states('draft'))
        self.assertTrue(self.scrap_order_produce.check_states('confirmed'))
        self.assertFalse(self.scrap_order_produce.check_states('done'))
        self.assertEqual(self.location_scrap.get_item_quantity(self.item), 0)
        self.assertEqual(self.location_produce.get_item_quantity(self.item), -1)
        self.assertFalse(self.scrap_order_produce.procurement.check_states('done'))

        self.scrap_produce_move.to_location = self.location_scrap
        self.scrap_produce_move.save()
        self.scrap_produce_move.done()
        self.assertFalse(self.scrap_order_produce.check_states('draft'))
        self.assertFalse(self.scrap_order_produce.check_states('confirmed'))
        self.assertTrue(self.scrap_order_produce.check_states('done'))
        self.assertEqual(self.location_scrap.get_item_quantity(self.item), 1)
        self.assertEqual(self.location_produce.get_item_quantity(self.item), -1)
        self.assertTrue(self.scrap_order_produce.procurement.check_states('done'))

    def test_stock_confirm_to_done(self):
        self.assertTrue(self.scrap_order_stock.check_states('draft'))
        self.assertFalse(self.scrap_order_stock.check_states('confirmed'))
        self.assertFalse(self.scrap_order_stock.check_states('done'))
        self.assertEqual(self.location_scrap.get_item_quantity(self.item), 0)
        self.assertEqual(self.location_stock.get_item_quantity(self.item), 0)
        self.assertEqual(self.scrap_order_stock.state, 'draft')

        self.assertEqual(self.scrap_order_stock.confirm(), self.scrap_order_stock)
        self.scrap_produce_move = self.scrap_order_stock.scraporderline_set.first().detail.doing_move
        self.assertFalse(self.scrap_order_stock.check_states('draft'))
        self.assertTrue(self.scrap_order_stock.check_states('confirmed'))
        self.assertFalse(self.scrap_order_stock.check_states('done'))
        self.assertEqual(self.location_scrap.get_item_quantity(self.item), 0)
        self.assertEqual(self.location_stock.get_item_quantity(self.item), -1)
        self.assertFalse(self.scrap_order_stock.procurement.check_states('done'))

        self.scrap_produce_move.to_location = self.location_scrap
        self.scrap_produce_move.save()
        self.scrap_produce_move.done()
        self.assertFalse(self.scrap_order_stock.check_states('draft'))
        self.assertFalse(self.scrap_order_stock.check_states('confirmed'))
        self.assertTrue(self.scrap_order_stock.check_states('done'))
        self.assertEqual(self.location_scrap.get_item_quantity(self.item), 1)
        self.assertEqual(self.location_stock.get_item_quantity(self.item), -1)
        self.assertTrue(self.scrap_order_stock.procurement.check_states('done'))

    def test_pack_confirm_to_done(self):
        self.assertTrue(self.scrap_order_pack.check_states('draft'))
        self.assertFalse(self.scrap_order_pack.check_states('confirmed'))
        self.assertFalse(self.scrap_order_pack.check_states('done'))
        self.assertEqual(self.location_scrap.get_item_quantity(self.item), 0)
        self.assertEqual(self.location_pack.get_item_quantity(self.item), 0)
        self.assertEqual(self.scrap_order_pack.state, 'draft')

        self.assertEqual(self.scrap_order_pack.confirm(), self.scrap_order_pack)
        self.scrap_produce_move = self.scrap_order_pack.scraporderline_set.first().detail.doing_move
        self.assertFalse(self.scrap_order_pack.check_states('draft'))
        self.assertTrue(self.scrap_order_pack.check_states('confirmed'))
        self.assertFalse(self.scrap_order_pack.check_states('done'))
        self.assertEqual(self.location_scrap.get_item_quantity(self.item), 0)
        self.assertEqual(self.location_pack.get_item_quantity(self.item), -1)
        self.assertFalse(self.scrap_order_pack.procurement.check_states('done'))

        self.scrap_produce_move.to_location = self.location_scrap
        self.scrap_produce_move.save()
        self.scrap_produce_move.done()
        self.assertFalse(self.scrap_order_pack.check_states('draft'))
        self.assertFalse(self.scrap_order_pack.check_states('confirmed'))
        self.assertTrue(self.scrap_order_pack.check_states('done'))
        self.assertEqual(self.location_scrap.get_item_quantity(self.item), 1)
        self.assertEqual(self.location_pack.get_item_quantity(self.item), -1)
        self.assertTrue(self.scrap_order_pack.procurement.check_states('done'))

    def test_repair_confirm_to_done(self):
        self.assertTrue(self.scrap_order_check.check_states('draft'))
        self.assertFalse(self.scrap_order_check.check_states('confirmed'))
        self.assertFalse(self.scrap_order_check.check_states('done'))
        self.assertEqual(self.location_scrap.get_item_quantity(self.item), 0)
        self.assertEqual(self.location_check.get_item_quantity(self.item), 0)
        self.assertEqual(self.scrap_order_check.state, 'draft')

        self.assertEqual(self.scrap_order_check.confirm(), self.scrap_order_check)
        self.scrap_produce_move = self.scrap_order_check.scraporderline_set.first().detail.doing_move
        self.assertFalse(self.scrap_order_check.check_states('draft'))
        self.assertTrue(self.scrap_order_check.check_states('confirmed'))
        self.assertFalse(self.scrap_order_check.check_states('done'))
        self.assertEqual(self.location_scrap.get_item_quantity(self.item), 0)
        self.assertEqual(self.location_check.get_item_quantity(self.item), -1)
        self.assertFalse(self.scrap_order_check.procurement.check_states('done'))

        self.scrap_produce_move.to_location = self.location_scrap
        self.scrap_produce_move.save()
        self.scrap_produce_move.done()
        self.assertFalse(self.scrap_order_check.check_states('draft'))
        self.assertFalse(self.scrap_order_check.check_states('confirmed'))
        self.assertTrue(self.scrap_order_check.check_states('done'))
        self.assertEqual(self.location_scrap.get_item_quantity(self.item), 1)
        self.assertEqual(self.location_check.get_item_quantity(self.item), -1)
        self.assertTrue(self.scrap_order_check.procurement.check_states('done'))
        self.assertFalse(self.scrap_order_pack.check_states('confirmed'))


class CloseoutOrderTestCase(EnvSetUpTestCase):
    def setUp(self):
        self.accountSetUp()
        self.productSetUp()
        self.stockSetUp()
        self.stock_order = models.CloseoutOrder.objects.create(
            location=self.location_stock,
            create_user=self.super_user
        )
        models.CloseoutOrderLine.objects.create(
            order=self.stock_order,
            item=self.item,
            quantity=1
        )

    def test_confirm(self):
        self.assertEqual(self.location_stock.get_item_quantity(self.item),0)
        self.assertEqual(self.location_closeout.get_item_quantity(self.item),0)
        self.stock_order.confirm()
        self.assertEqual(self.location_stock.get_item_quantity(self.item), -1)
        self.assertEqual(self.location_closeout.get_item_quantity(self.item), 1)






class WarehouseTestCase(EnvSetUpTestCase):
    def setUp(self):
        self.accountSetUp()
        self.productSetUp()
        self.stockSetUp()
        self.procurement = models.Procurement.objects.create(warehouse=self.warehouse, user=self.super_user)
        self.procurement_detail = models.ProcurementDetail.objects.create(
            item=self.item,
            procurement=self.procurement,
            quantity=D('5'),
            route=self.route
        )
        self.procurement.confirm()
        self.procurement_detail.start()
        self.move = self.procurement_detail.move_set.first()

    def test_get_root_location(self):
        for usage in models.Location.INDIVISIBLE_USAGE:
            self.assertEqual(self.warehouse.get_root_location(usage).zone, usage)
            self.assertFalse(self.warehouse.get_root_location(usage).is_virtual)

    def test_move_transfer(self):
        self.move.to_location = self.location_pack
        self.move.save()
        print(self.move)
        # at produce lock 5
        self.assertEqual(self.location_produce.get_item_quantity(self.item), D('-5'))
        self.assertEqual(self.location_pack.get_item_quantity(self.item), D('0'))
        self.assertEqual(self.location_check.get_item_quantity(self.item), D('0'))
        self.assertEqual(self.location_wait.get_item_quantity(self.item), D('0'))
        self.assertEqual(self.location_stock.get_item_quantity(self.item), D('0'))
        self.assertEqual(self.item.cache.all(), D('0'))
        self.assertEqual(self.item.cache.settled(), D('0'))
        self.assertEqual(self.item.cache.transporting(), D('0'))
        self.assertEqual(self.move.done(), self.move)
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
        print(self.next_move.to_location, self.next_move.from_route_setting.location)
        self.assertEqual(self.next_move.done(), self.next_move)
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
        self.assertEqual(self.next_move.done(), self.next_move)
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

        self.assertEqual(self.procurement.cancel(), self.procurement)
        self.assertEqual(self.next_move.done(), self.next_move)
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
        self.assertEqual(self.next_move.done(), self.next_move)
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
        self.assertEqual(self.next_move.done(), self.next_move)
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
        self.assertEqual(self.next_move.done(), self.next_move)
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
        self.assertEqual(self.next_move.done(), self.next_move)
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
