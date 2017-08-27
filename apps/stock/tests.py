#!/usr/bin/env python3
#-*- coding:utf-8 -*-

from decimal import Decimal as D
from common.test import EnvSetUpTestCase
from common.exceptions import NotInStates

class WarehouseTestCase(EnvSetUpTestCase):

    def test_move_transfer(self):
        # at produce lock 0
        print(self.move)
        self.assertEqual(self.location_produce.get_item_quantity(self.item), D('0'))
        self.assertEqual(self.location_pack.get_item_quantity(self.item), D('0'))
        self.assertEqual(self.location_check.get_item_quantity(self.item), D('0'))
        self.assertEqual(self.location_pick.get_item_quantity(self.item), D('0'))
        self.assertEqual(self.location_stock.get_item_quantity(self.item), D('0'))
        self.assertEqual(self.move.confirm(),self.move)
        # at produce lock 5
        self.assertEqual(self.location_produce.get_item_quantity(self.item),D('-5'))
        self.assertEqual(self.location_pack.get_item_quantity(self.item),D('0'))
        self.assertEqual(self.location_check.get_item_quantity(self.item),D('0'))
        self.assertEqual(self.location_pick.get_item_quantity(self.item), D('0'))
        self.assertEqual(self.location_stock.get_item_quantity(self.item), D('0'))
        self.assertEqual(self.item.cache.all,D('0'))
        self.assertEqual(self.item.cache.settled,D('0'))
        self.assertEqual(self.item.cache.transporting,D('0'))
        self.assertEqual(self.move.done(next_location=self.location_check),self.move)
        # at pack lock 0
        self.assertFalse(self.procurement.check_states('done'))
        with self.assertRaises(NotInStates):
            self.move.done()
        with self.assertRaises(NotInStates):
            self.move.done(next_location=self.location_check)

        self.next_move = self.move.to_move
        print(self.next_move)
        self.assertEqual(self.next_move.confirm(),self.next_move)
        # at pack lock 5
        self.assertEqual(self.location_produce.get_item_quantity(self.item), D('-5'))
        self.assertEqual(self.location_pack.get_item_quantity(self.item), D('0'))
        self.assertEqual(self.location_check.get_item_quantity(self.item), D('0'))
        self.assertEqual(self.location_pick.get_item_quantity(self.item), D('0'))
        self.assertEqual(self.location_stock.get_item_quantity(self.item), D('0'))
        self.assertEqual(self.item.cache.all, D('5'))
        self.assertEqual(self.item.cache.settled, D('0'))
        self.assertEqual(self.item.cache.transporting, D('5'))
        self.assertEqual(self.next_move.done(next_location=self.location_pick),self.next_move)
        # at check lock 0
        self.assertFalse(self.procurement.check_states('done'))
        with self.assertRaises(NotInStates):
            self.move.done()
        with self.assertRaises(NotInStates):
            self.move.done(next_location=self.location_check)

        self.next_move = self.next_move.to_move
        print(self.next_move)
        self.assertEqual(self.next_move.confirm(), self.next_move)
        # at check lock 5
        self.assertEqual(self.location_produce.get_item_quantity(self.item), D('-5'))
        self.assertEqual(self.location_pack.get_item_quantity(self.item), D('0'))
        self.assertEqual(self.location_check.get_item_quantity(self.item), D('0'))
        self.assertEqual(self.location_pick.get_item_quantity(self.item), D('0'))
        self.assertEqual(self.location_stock.get_item_quantity(self.item), D('0'))
        self.assertEqual(self.item.cache.all, D('5'))
        self.assertEqual(self.item.cache.settled, D('0'))
        self.assertEqual(self.item.cache.transporting, D('5'))
        self.assertEqual(self.next_move.done(next_location=self.location_stock),self.next_move)
        # at pick lock 0
        self.assertFalse(self.procurement.check_states('done'))
        with self.assertRaises(NotInStates):
            self.move.done()
        with self.assertRaises(NotInStates):
            self.move.done(next_location=self.location_check)

        self.next_move = self.next_move.to_move
        print(self.next_move)
        self.assertEqual(self.next_move.confirm(), self.next_move)
        # at pick lock 5
        self.assertEqual(self.location_produce.get_item_quantity(self.item), D('-5'))
        self.assertEqual(self.location_pack.get_item_quantity(self.item), D('0'))
        self.assertEqual(self.location_check.get_item_quantity(self.item), D('0'))
        self.assertEqual(self.location_pick.get_item_quantity(self.item), D('0'))
        self.assertEqual(self.location_stock.get_item_quantity(self.item), D('0'))
        self.assertEqual(self.item.cache.all, D('5'))
        self.assertEqual(self.item.cache.settled, D('0'))
        self.assertEqual(self.item.cache.transporting, D('5'))

        self.assertEqual(self.procurement.cancel(),self.procurement)
        self.assertEqual(self.next_move.done(next_location=self.location_pick),self.next_move)
        # at stock lock 0
        self.assertFalse(self.procurement.check_states('done'))
        self.assertTrue(self.procurement.check_states('cancel'))
        with self.assertRaises(NotInStates):
            self.move.done()
        with self.assertRaises(NotInStates):
            self.move.done(next_location=self.location_check)

        self.next_move = self.next_move.to_move
        print(self.next_move)
        self.assertEqual(self.next_move.confirm(), self.next_move)
        # at stock lock 5
        self.assertEqual(self.location_produce.get_item_quantity(self.item), D('-5'))
        self.assertEqual(self.location_pack.get_item_quantity(self.item), D('0'))
        self.assertEqual(self.location_check.get_item_quantity(self.item), D('0'))
        self.assertEqual(self.location_pick.get_item_quantity(self.item), D('0'))
        self.assertEqual(self.location_stock.get_item_quantity(self.item), D('0'))
        self.assertEqual(self.item.cache.all, D('5'))
        self.assertEqual(self.item.cache.settled, D('0'))
        self.assertEqual(self.item.cache.transporting, D('0'))
        self.assertEqual(self.next_move.done(next_location=self.location_check),self.next_move)
        # at pick lock 0
        self.assertTrue(self.procurement.check_states('cancel'))
        with self.assertRaises(NotInStates):
            self.move.done()
        with self.assertRaises(NotInStates):
            self.move.done(next_location=self.location_check)

        self.next_move = self.next_move.to_move
        print(self.next_move)
        self.assertEqual(self.next_move.confirm(), self.next_move)
        # at pick lock 5
        self.assertEqual(self.location_produce.get_item_quantity(self.item), D('-5'))
        self.assertEqual(self.location_pack.get_item_quantity(self.item), D('0'))
        self.assertEqual(self.location_check.get_item_quantity(self.item), D('0'))
        self.assertEqual(self.location_pick.get_item_quantity(self.item), D('0'))
        self.assertEqual(self.location_stock.get_item_quantity(self.item), D('0'))
        self.assertEqual(self.item.cache.all, D('5'))
        self.assertEqual(self.item.cache.settled, D('0'))
        self.assertEqual(self.item.cache.transporting, D('5'))
        self.assertEqual(self.next_move.done(next_location=self.location_pack),self.next_move)
        # at check lock 0
        self.assertTrue(self.procurement.check_states('cancel'))
        with self.assertRaises(NotInStates):
            self.move.done()
        with self.assertRaises(NotInStates):
            self.move.done(next_location=self.location_check)

        self.next_move = self.next_move.to_move
        print(self.next_move)
        self.assertEqual(self.next_move.confirm(), self.next_move)
        # at check lock 5
        self.assertEqual(self.location_produce.get_item_quantity(self.item), D('-5'))
        self.assertEqual(self.location_pack.get_item_quantity(self.item), D('0'))
        self.assertEqual(self.location_check.get_item_quantity(self.item), D('0'))
        self.assertEqual(self.location_pick.get_item_quantity(self.item), D('0'))
        self.assertEqual(self.location_stock.get_item_quantity(self.item), D('0'))
        self.assertEqual(self.item.cache.all, D('5'))
        self.assertEqual(self.item.cache.settled, D('0'))
        self.assertEqual(self.item.cache.transporting, D('5'))
        self.assertEqual(self.next_move.done(next_location=self.location_produce),self.next_move)
        # at pack lock 0
        self.assertTrue(self.procurement.check_states('cancel'))
        with self.assertRaises(NotInStates):
            self.move.done()
        with self.assertRaises(NotInStates):
            self.move.done(next_location=self.location_check)

        self.next_move = self.next_move.to_move
        print(self.next_move)
        self.assertEqual(self.next_move.confirm(), self.next_move)
        # at pack lock 5
        self.assertEqual(self.location_produce.get_item_quantity(self.item), D('-5'))
        self.assertEqual(self.location_pack.get_item_quantity(self.item), D('0'))
        self.assertEqual(self.location_check.get_item_quantity(self.item), D('0'))
        self.assertEqual(self.location_pick.get_item_quantity(self.item), D('0'))
        self.assertEqual(self.location_stock.get_item_quantity(self.item), D('0'))
        self.assertEqual(self.item.cache.all, D('5'))
        self.assertEqual(self.item.cache.settled, D('0'))
        self.assertEqual(self.item.cache.transporting, D('5'))
        self.assertEqual(self.next_move.done(),self.next_move)
        # at produce lock 0
        self.assertTrue(self.procurement.check_states('cancel'))
        with self.assertRaises(NotInStates):
            self.move.done()
        with self.assertRaises(NotInStates):
            self.move.done(next_location=self.location_check)

        self.assertEqual(self.location_produce.get_item_quantity(self.item), D('0'))
        self.assertEqual(self.location_pack.get_item_quantity(self.item), D('0'))
        self.assertEqual(self.location_check.get_item_quantity(self.item), D('0'))
        self.assertEqual(self.location_pick.get_item_quantity(self.item), D('0'))
        self.assertEqual(self.location_stock.get_item_quantity(self.item), D('0'))
        self.assertEqual(self.item.cache.all, D('0'))
        self.assertEqual(self.item.cache.settled, D('0'))
        self.assertEqual(self.item.cache.transporting, D('0'))

    def test_location_tree(self):
        self.assertTrue(self.location_stock.all_parent_nodes)
        self.assertFalse(self.location_stock.all_child_nodes)
        self.assertEqual(self.location_stock.root_node,self.zone_stock.root_location)
        self.assertEqual(self.location_stock.all_parent_nodes.first(),self.zone_stock.root_location)
        self.assertEqual(self.zone_stock.root_location.all_child_nodes.first(),self.location_stock)
        self.assertFalse(self.location_stock.sibling_nodes)