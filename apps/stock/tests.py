#!/usr/bin/env python3
#-*- coding:utf-8 -*-

from decimal import Decimal as D
from common.test import EnvSetUpTestCase

class WarehouseTestCase(EnvSetUpTestCase):

    def test_signal_refresh_product_quantity(self):

        self.assertTrue(self.move.confirm())
        self.assertEqual(self.location_initial.get_item_quantity(self.item),D('-5'))
        self.assertEqual(self.location_pick.get_item_quantity(self.item),D('0'))
        self.assertEqual(self.location_stock.get_item_quantity(self.item),D('0'))
        self.assertEqual(self.item.cache.all,D('0'))
        self.assertEqual(self.item.cache.settled,D('0'))
        self.assertEqual(self.item.cache.transporting,D('0'))
        self.assertTrue(self.move.done(next_location=self.location_stock))
        self.assertFalse(self.procurement.check_states('done'))
        self.assertEqual(self.item.cache.all, D('5'))
        self.assertEqual(self.item.cache.settled, D('0'))
        self.assertEqual(self.item.cache.transporting, D('5'))

        self.next_move = self.move.to_moves.first()
        self.assertTrue(self.next_move.confirm())
        self.assertEqual(self.location_initial.get_item_quantity(self.product), D('-5'))
        self.assertEqual(self.location_pick.get_item_quantity(self.product), D('0'))
        self.assertEqual(self.location_stock.get_item_quantity(self.product), D('0'))
        self.assertEqual(self.item.cache.all, D('5'))
        self.assertEqual(self.item.cache.settled, D('0'))
        self.assertEqual(self.item.cache.transporting, D('5'))
        self.assertTrue(self.next_move.done())
        self.assertTrue(self.procurement.check_states('done'))

        self.assertEqual(self.location_initial.get_item_quantity(self.product),D('-5'))
        self.assertEqual(self.location_pick.get_item_quantity(self.product),D('0'))
        self.assertEqual(self.location_stock.get_item_quantity(self.product),D('5'))
        self.assertEqual(self.item.cache.all,D('5'))
        self.assertEqual(self.item.cache.settled,D('0'))
        self.assertEqual(self.item.cache.transporting,D('0'))

    def test_location_tree(self):
        self.assertTrue(self.location_initial.all_parent_nodes)
        self.assertFalse(self.location_initial.all_child_nodes)
        self.assertEqual(self.location_initial.root_node,self.zone_initial.root_location)
        self.assertEqual(self.location_initial.all_parent_nodes.first(),self.zone_initial.root_location)
        self.assertEqual(self.zone_initial.root_location.all_child_nodes.first(),self.location_initial)
        self.assertFalse(self.location_initial.sibling_nodes)


