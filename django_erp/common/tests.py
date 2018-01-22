#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
@author:    olinex
@time:      2017/8/29 上午12:52
"""

__all__ = [
    'AbstractTestCase',
    'BaseModelTestCase',
    'DataModelTestCase'
]

from django.test import tag
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError

User = get_user_model()


class AbstractTestCase(object):
    def assertAlmostEqual(self, first, second, places=None, msg=None, delta=None):
        pass

    def assertContains(self, response, text, count=None, status_code=200, msg_prefix='', html=False):
        pass

    def assertCountEqual(self, first, second, msg=None):
        pass

    def assertEqual(self, first, second, msg=None):
        pass

    def assertDictEqual(self, d1, d2, msg=None):
        pass

    def assertDictContainsSubset(self, subset, dictionary, msg=None):
        pass

    def assertFalse(self, expr, msg=None):
        pass

    def assertFieldOutput(self, fieldclass, valid, invalid, field_args=None, field_kwargs=None, empty_value=''):
        pass

    def assertFormError(self, response, form, field, errors, msg_prefix=''):
        pass

    def assertFormsetError(self, response, formset, form_index, field, errors, msg_prefix=''):
        pass

    def assertGreater(self, a, b, msg=None):
        pass

    def assertGreaterEqual(self, a, b, msg=None):
        pass

    def assertHTMLEqual(self, html1, html2, msg=None):
        pass

    def assertHTMLNotEqual(self, html1, html2, msg=None):
        pass

    def assertIn(self, member, container, msg=None):
        pass

    def assertInHTML(self, needle, haystack, count=None, msg_prefix=''):
        pass

    def assertIs(self, expr1, expr2, msg=None):
        pass

    def assertIsInstance(self, obj, cls, msg=None):
        pass

    def assertIsNone(self, obj, msg=None):
        pass

    def assertIsNot(self, expr1, expr2, msg=None):
        pass

    def assertIsNotNone(self, obj, msg=None):
        pass

    def assertJSONEqual(self, raw, expected_data, msg=None):
        pass

    def assertJSONNotEqual(self, raw, expected_data, msg=None):
        pass

    def assertLess(self, a, b, msg=None):
        pass

    def assertLessEqual(self, a, b, msg=None):
        pass

    def assertListEqual(self, list1, list2, msg=None):
        pass

    def assertLogs(self, logger=None, level=None):
        pass

    def assertMultiLineEqual(self, first, second, msg=None):
        pass

    def assertNotAlmostEqual(self, first, second, places=None, msg=None, delta=None):
        pass

    def assertNotContains(self, response, text, status_code=200, msg_prefix='', html=False):
        pass

    def assertNotEqual(self, first, second, msg=None):
        pass

    def assertNotIn(self, member, container, msg=None):
        pass

    def assertNotIsInstance(self, obj, cls, msg=None):
        pass

    def assertNotRegex(self, text, unexpected_regex, msg=None):
        pass

    def assertNumQueries(self, num, func=None, *args, **kwargs):
        pass

    def assertQuerysetEqual(self, qs, values, transform=repr, ordered=True, msg=None):
        pass

    def assertRaises(self, expected_exception, *args, **kwargs):
        pass

    def assertRaisesMessage(self, expected_exception, expected_message, *args, **kwargs):
        pass

    def assertRaisesRegex(self, expected_exception, expected_regex,
                          *args, **kwargs):
        pass

    def assertRedirects(self, response, expected_url, status_code=302,
                        target_status_code=200, host=None, msg_prefix='',
                        fetch_redirect_response=True):
        pass

    def assertRegex(self, text, expected_regex, msg=None):
        pass

    def assertSequenceEqual(self, seq1, seq2, msg=None, seq_type=None):
        pass

    def assertSetEqual(self, set1, set2, msg=None):
        pass

    def assertTemplateNotUsed(self, response=None, template_name=None, msg_prefix=''):
        pass

    def assertTemplateUsed(self, response=None, template_name=None, msg_prefix='', count=None):
        pass

    def assertTrue(self, expr, msg=None):
        pass

    def assertTupleEqual(self, tuple1, tuple2, msg=None):
        pass

    def assertWarns(self, expected_warning, *args, **kwargs):
        pass

    def assertWarnsRegex(self, expected_warning, expected_regex,
                         *args, **kwargs):
        pass

    def assertXMLEqual(self, xml1, xml2, msg=None):
        pass

    def assertXMLNotEqual(self, xml1, xml2, msg=None):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def tearDownClass(cls):
        pass

    def settings(self, **kwargs):
        pass

    def setUpClass(cls):
        pass

    def setUpTestData(cls):
        pass

    def userSetup(self):
        import random
        import string
        from django.contrib.auth.models import AnonymousUser
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

    def userTearDown(self):
        self.super_user.clear_messages()
        self.normal_user.clear_messages()


class BaseModelTestCase(AbstractTestCase):
    model = None

    def setUp(self):
        self.instance1 = self.model.objects.create()
        self.instance2 = self.model.objects.create()

    @tag('buildin')
    def test_check_singal_state(self):
        self.assertTrue(self.instance1.check_states('draft'))
        self.assertFalse(self.instance1.check_states('confirmed'))
        self.assertFalse(self.instance1.check_states('active'))
        self.assertFalse(self.instance1.check_states('locked'))

        self.assertTrue(self.instance2.check_states('draft'))
        self.assertFalse(self.instance2.check_states('confirmed'))
        self.assertFalse(self.instance2.check_states('active'))
        self.assertFalse(self.instance2.check_states('locked'))

    @tag('buildin')
    def test_check_multi_states(self):
        self.assertTrue(self.instance1.check_states('draft', 'confirmed'))
        self.assertFalse(self.instance1.check_states('confirmed', 'active'))
        self.assertTrue(self.instance2.check_states('draft', 'confirmed'))
        self.assertFalse(self.instance2.check_states('confirmed', 'active'))

    @tag('buildin')
    def test_statement(self):
        self.assertTrue(self.instance1.States.draft.kwargs['is_draft'])
        self.assertTrue(self.instance2.States.draft.kwargs['is_draft'])

        self.assertFalse(self.instance1.States.confirmed.kwargs['is_draft'])
        self.assertFalse(self.instance2.States.confirmed.kwargs['is_draft'])

        self.assertFalse(self.instance1.States.active.kwargs['is_draft'])
        self.assertFalse(self.instance2.States.active.kwargs['is_draft'])
        self.assertTrue(self.instance1.States.active.kwargs['is_active'])
        self.assertTrue(self.instance2.States.active.kwargs['is_active'])

        self.assertFalse(self.instance1.States.locked.kwargs['is_draft'])
        self.assertFalse(self.instance2.States.locked.kwargs['is_draft'])
        self.assertFalse(self.instance1.States.locked.kwargs['is_active'])
        self.assertFalse(self.instance2.States.locked.kwargs['is_active'])

    @tag('buildin')
    def test_check_states_queryset(self):
        self.assertTrue(self.model.check_states_queryset('draft', queryset=self.model.objects.all()))
        self.assertFalse(self.model.check_states_queryset('confirmed', queryset=self.model.objects.all()))
        self.assertFalse(self.model.check_states_queryset('active', queryset=self.model.objects.all()))
        self.assertFalse(self.model.check_states_queryset('locked', queryset=self.model.objects.all()))

    @tag('buildin')
    def test_get_states_queryset(self):
        self.assertTrue(self.model.get_states_queryset('draft').exists())
        self.assertFalse(self.model.get_states_queryset('confirmed').exists())
        self.assertFalse(self.model.get_states_queryset('active').exists())
        self.assertFalse(self.model.get_states_queryset('locked').exists())

    @tag('buildin')
    def test_action_confirm(self):
        self.assertIsNone(self.instance1.action_confirm(user=self.super_user))

        self.assertFalse(self.instance1.check_states('draft'))
        self.assertTrue(self.instance1.check_states('confirmed'))
        self.assertTrue(self.instance1.check_states('active'))
        self.assertFalse(self.instance1.check_states('locked'))

        self.assertTrue(self.instance2.check_states('draft'))
        self.assertFalse(self.instance2.check_states('confirmed'))
        self.assertFalse(self.instance2.check_states('active'))
        self.assertFalse(self.instance2.check_states('locked'))
        with self.assertRaises(ValidationError):
            self.instance1.action_confirm(user=self.super_user,raise_exception=True)

    @tag('buildin')
    def test_action_lock(self):
        self.assertIsNone(self.instance1.action_confirm(user=self.super_user))
        self.assertIsNone(self.instance1.action_lock(user=self.super_user))

        self.assertFalse(self.instance1.check_states('draft'))
        self.assertTrue(self.instance1.check_states('confirmed'))
        self.assertFalse(self.instance1.check_states('active'))
        self.assertTrue(self.instance1.check_states('locked'))

        self.assertTrue(self.instance2.check_states('draft'))
        self.assertFalse(self.instance2.check_states('confirmed'))
        self.assertFalse(self.instance2.check_states('active'))
        self.assertFalse(self.instance2.check_states('locked'))
        with self.assertRaises(ValidationError):
            self.instance1.action_confirm(user=self.super_user,raise_exception=True)
            self.instance1.action_lock(user=self.super_user,raise_exception=True)

    @tag('buildin')
    def test_action_active(self):
        self.assertIsNone(self.instance1.action_confirm(user=self.super_user))
        self.assertIsNone(self.instance1.action_lock(user=self.super_user))
        self.assertIsNone(self.instance1.action_active(user=self.super_user))

        self.assertFalse(self.instance1.check_states('draft'))
        self.assertTrue(self.instance1.check_states('confirmed'))
        self.assertTrue(self.instance1.check_states('active'))
        self.assertFalse(self.instance1.check_states('locked'))

        self.assertTrue(self.instance2.check_states('draft'))
        self.assertFalse(self.instance2.check_states('confirmed'))
        self.assertFalse(self.instance2.check_states('active'))
        self.assertFalse(self.instance2.check_states('locked'))
        with self.assertRaises(ValidationError):
            self.instance1.action_confirm(user=self.super_user,raise_exception=True)
            self.instance1.action_active(user=self.super_user,raise_exception=True)

    @tag('buildin')
    def test_action_delete(self):
        self.assertIsNone(self.instance1.action_delete(user=self.super_user))
        self.assertFalse(self.model.objects.filter(pk=self.instance1.pk).exists())
        self.assertTrue(self.model.objects.filter(pk=self.instance2.pk).exists())


class DataModelTestCase(BaseModelTestCase):
    @tag('buildin')
    def test_sequence_order_by(self):
        self.assertListEqual(
            list(self.model.objects.all()),
            list(self.model.objects.all().order_by('sequence'))
        )

# class EnvSetUpTestCase(TestCase):
#     def accountSetUp(self):
#         self.password = ''.join(random.sample(string.ascii_letters, 10))
#         self.super_user = User.objects.create_superuser(
#             username='test_super_user',
#             email='demosuperuser@163.com',
#             password=self.password)
#         self.normal_user = User.objects.create_user(
#             username='test_normal_user',
#             email='demouser@163.com',
#             password=self.password)
#         self.anon_user = AnonymousUser()
#         self.province = Province.objects.create(
#             country='China',
#             name='province_test'
#         )
#         self.city = City.objects.create(
#             province=self.province,
#             name='city_test'
#         )
#         self.region = Region.objects.create(
#             city=self.city,
#             name='region_test'
#         )
#         self.address = Address.objects.create(
#             region=self.region,
#             name='address_test'
#         )
#         self.partner = Partner.objects.create(
#             name='partner_test',
#             phone='12342342342'
#         )
#
#     def productSetUp(self):
#         self.category = ProductCategory.objects.create(
#             name='category_test'
#         )
#         self.uom = UOM.objects.create(
#             name='uom_test',
#             symbol='uom',
#             ratio=D('0.01'),
#             category='m'
#         )
#         self.attr = Attribute.objects.create(
#             name='attr_test',
#             value=[1, 2, 3, 4],
#             extra_price=[1, 2, 3, 4]
#         )
#         self.template = ProductTemplate.objects.create(
#             name='template_test',
#             stock_type='stock-no-expiration',
#             uom=self.uom,
#             category=self.category
#         )
#         self.template.attributes.add(self.attr)
#         self.product = self.template.product_set.first()
#         self.item = self.product.item
#         self.item.__class__ = Item
#         self.lot = Lot.objects.create(
#             name='lot_test',
#             product=self.product
#         )
#         self.package_type = PackageType.objects.create(
#             name='package_type_test'
#         )
#         PackageTypeSetting.objects.bulk_create([
#             PackageTypeSetting(
#                 package_type=self.package_type,
#                 item=product.item,
#                 max_quantity=10
#             ) for product in self.template.product_set.all()
#         ])
#         self.package_template = PackageTemplate.objects.create(
#             name='package_template_test',
#             package_type=self.package_type
#         )
#         PackageTemplateSetting.objects.bulk_create([
#             PackageTemplateSetting(
#                 package_template=self.package_template,
#                 type_setting=setting,
#                 quantity=9
#             ) for setting in self.package_type.packagetypesetting_set.all()
#         ])
#         self.package_node = PackageNode.objects.create(
#             template=self.package_template,
#             quantity=1
#         )
#
#     def stockSetUp(self):
#         self.warehouse = Warehouse.objects.create(
#             name='warehouse_1',
#             manager=self.super_user,
#             address=self.address
#         )
#         self.location_root = self.warehouse.root_location
#         self.location_stock = Location.objects.create(
#             warehouse=self.warehouse,
#             zone='stock',
#             is_virtual=False,
#             x='0', y='0', z='0'
#         )
#         self.location_pack = Location.objects.create(
#             warehouse=self.warehouse,
#             zone='pack',
#             is_virtual=False,
#             x='0', y='0', z='0'
#         )
#         self.location_check = Location.objects.create(
#             warehouse=self.warehouse,
#             zone='check',
#             is_virtual=False,
#             x='0', y='0', z='0'
#         )
#         self.location_wait = Location.objects.create(
#             warehouse=self.warehouse,
#             zone='wait',
#             is_virtual=False,
#             x='0', y='0', z='0'
#         )
#         self.location_deliver = Location.objects.create(
#             warehouse=self.warehouse,
#             zone='deliver',
#             is_virtual=False,
#             x='0', y='0', z='0'
#         )
#         self.location_customer = Location.objects.create(
#             warehouse=self.warehouse,
#             zone='customer',
#             is_virtual=False,
#             x='0', y='0', z='0'
#         )
#         self.location_supplier = Location.objects.create(
#             warehouse=self.warehouse,
#             zone='supplier',
#             is_virtual=False,
#             x='0', y='0', z='0'
#         )
#         self.location_produce = Location.objects.create(
#             warehouse=self.warehouse,
#             zone='produce',
#             is_virtual=False,
#             x='0', y='0', z='0'
#         )
#         self.location_repair = Location.objects.create(
#             warehouse=self.warehouse,
#             zone='repair',
#             is_virtual=False,
#             x='0', y='0', z='0'
#         )
#         self.location_scrap = Location.objects.create(
#             warehouse=self.warehouse,
#             zone='scrap',
#             is_virtual=False,
#             x='0', y='0', z='0'
#         )
#         self.location_closeout = self.warehouse.closeout_location
#         self.location_initial = self.warehouse.initial_location
#
#         self.location_stock.change_parent_node(self.warehouse.get_root_location('stock'))
#         self.location_pack.change_parent_node(self.warehouse.get_root_location('pack'))
#         self.location_check.change_parent_node(self.warehouse.get_root_location('check'))
#         self.location_wait.change_parent_node(self.warehouse.get_root_location('wait'))
#         self.location_deliver.change_parent_node(self.warehouse.get_root_location('deliver'))
#         self.location_customer.change_parent_node(self.warehouse.get_root_location('customer'))
#         self.location_supplier.change_parent_node(self.warehouse.get_root_location('supplier'))
#         self.location_produce.change_parent_node(self.warehouse.get_root_location('produce'))
#         self.location_repair.change_parent_node(self.warehouse.get_root_location('repair'))
#         self.location_scrap.change_parent_node(self.warehouse.get_root_location('scrap'))
#
#         self.location_stock.cache.sync()
#         self.location_pack.cache.sync()
#         self.location_check.cache.sync()
#         self.location_wait.cache.sync()
#         self.location_deliver.cache.sync()
#         self.location_customer.cache.sync()
#         self.location_supplier.cache.sync()
#         self.location_produce.cache.sync()
#         self.location_repair.cache.sync()
#         self.location_scrap.cache.sync()
#         self.location_closeout.cache.sync()
#         self.location_initial.cache.sync()
#
#         self.item.cache.sync()
#
#         self.route = Route.objects.create(
#             name='route_test',
#             warehouse=self.warehouse,
#             sequence=1
#         )
#         RouteSetting.objects.bulk_create([
#             RouteSetting(
#                 name=str(index),
#                 route=self.route,
#                 location=getattr(self, location),
#                 sequence=index + 1
#             ) for index, location in enumerate(['location_pack', 'location_check', 'location_wait'])
#         ])
#         RouteSetting.objects.create(name='initial', route=self.route, location=self.location_produce, sequence=0)
#         RouteSetting.objects.create(name='end', route=self.route, location=self.location_stock, sequence=10)
