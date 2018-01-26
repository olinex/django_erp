#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from .uom import *
from .attribute import *
from .product_category import *
from .product_template import *
from .product import *
from .lot import *

# from .utils import QuantityField
#
# from django.db import transaction
# from django.db.models import Manager, Q
# from django.contrib.auth import get_user_model
# from django.core.validators import MinValueValidator
# from django.utils.translation import ugettext_lazy as _
# from django.contrib.contenttypes.models import ContentType
# from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
# from django_perm import models
# from common.state import Statement, StateMachine
# from common.model import BaseModel, TreeModel
# from common.fields import ActiveLimitForeignKey
#
# User = get_user_model()
#
#
# class PackageType(BaseModel):
#     """
#     the type of package which define it name,the name must be unique
#     """
#
#     name = models.CharField(
#         _('name'),
#         null=False,
#         blank=False,
#         unique=True,
#         max_length=90,
#         help_text=_("the type name of package")
#     )
#
#     items = models.ManyToManyField(
#         'django_product.Item',
#         blank=False,
#         through='django_product.PackageTypeSetting',
#         through_fields=('package_type', 'item'),
#         verbose_name=_('items'),
#         help_text=_('the packable items of package')
#     )
#
#     def __str__(self):
#         return self.name
#
#     class Meta:
#         verbose_name = _('package type')
#         verbose_name_plural = _('package types')
#
#
# class PackageTypeSetting(models.Model, StateMachine):
#     """
#     Constraint sets the maximum number of packages
#     """
#
#     package_type = ActiveLimitForeignKey(
#         'django_product.PackageType',
#         null=False,
#         blank=False,
#         verbose_name=_('package type'),
#         help_text=_('the type of package which settings belongs to')
#     )
#
#     item = ActiveLimitForeignKey(
#         'django_product.Item',
#         null=False,
#         blank=False,
#         verbose_name=_('item'),
#         help_text=_('the item which can be packed in this type of package')
#     )
#
#     max_quantity = QuantityField(
#         _('max quantity'),
#         null=False,
#         blank=False,
#         uom='item.instance.uom',
#         validators=[MinValueValidator(0)],
#         help_text=_('the max quantity of item can be packed into package')
#     )
#
#     def __str__(self):
#         return '{}-{}({})'.format(
#             self.package_type,
#             self.item,
#             str(self.max_quantity)
#         )
#
#     class Meta:
#         verbose_name = _('setting of package type')
#         verbose_name_plural = _('settings of package type')
#         unique_together = (
#             ('package_type', 'item'),
#         )
#
#     class States:
#         product_setting = Statement(
#             Q(item__content_type__app_label='django_product') &
#             Q(item__content_type__model='Product')
#         )
#
#
# class PackageTemplate(BaseModel):
#     """
#     the template of package type
#     """
#
#     name = models.CharField(
#         _('name'),
#         null=False,
#         blank=False,
#         unique=True,
#         max_length=90,
#         help_text=_('the name of package template')
#     )
#
#     package_type = ActiveLimitForeignKey(
#         'django_product.PackageType',
#         null=False,
#         blank=False,
#         verbose_name=_('package type'),
#         help_text=_('the package type of this template,constraint max number of item')
#     )
#
#     type_settings = models.ManyToManyField(
#         'django_product.PackageTypeSetting',
#         blank=False,
#         through='django_product.PackageTemplateSetting',
#         through_fields=('package_template', 'type_setting'),
#         verbose_name=_('the type settings of package'),
#         help_text=_('the type settings of package which constraint max number of item')
#     )
#
#     def __str__(self):
#         return str(self.package_type)
#
#     class Meta:
#         verbose_name = _('package template')
#         verbose_name_plural = _('package templates')
#
#
# class PackageTemplateSetting(models.Model):
#     """
#     the setting which set the number of item in the package
#     """
#
#     package_template = ActiveLimitForeignKey(
#         'django_product.PackageTemplate',
#         null=False,
#         blank=False,
#         verbose_name=_('package template'),
#         help_text=_('the package template which setting belongs to')
#     )
#
#     type_setting = models.ForeignKey(
#         'django_product.PackageTypeSetting',
#         null=False,
#         blank=False,
#         verbose_name=_('package type setting'),
#         help_text=_('the package type setting will constraint the max number of item of this template setting')
#     )
#
#     quantity = QuantityField(
#         _('quantity'),
#         null=False,
#         blank=False,
#         uom='type_setting.uom',
#         validators=[MinValueValidator(0)],
#         help_text=_('the quantity of item in package template')
#     )
#
#     def __str__(self):
#         return '{}-{}({})'.format(
#             self.package_template,
#             self.type_setting,
#             str(self.quantity)
#         )
#
#     class Meta:
#         verbose_name = _('package template setting')
#         verbose_name_plural = _('package template settings')
#         unique_together = (
#             ('package_template', 'type_setting'),
#         )
#
#
# class PackageNode(TreeModel, StateMachine):
#     """
#     package node,every node contain an package template
#     """
#
#     template = ActiveLimitForeignKey(
#         'django_product.PackageTemplate',
#         null=False,
#         blank=False,
#         verbose_name=_('package template'),
#         help_text=_('package template in the package tree')
#     )
#
#     quantity = models.PositiveSmallIntegerField(
#         _('quantity'),
#         null=False,
#         blank=False,
#         help_text=_('the quantity of the template in this node')
#     )
#
#     items = GenericRelation('django_product.Item')
#
#     @property
#     def item(self):
#         if not hasattr(self, '__item'):
#             self.__item = self.items.first()
#         return self.__item
#
#     @property
#     def child_quantity_dict(self):
#         """
#         return the dict of all childs pk and quantity dict,
#         and an empty string with itself's quantity
#         :return: dict
#         """
#         result = dict(self.all_child_nodes.values_list('pk', 'quantity'))
#         return result
#
#     def __str__(self):
#         return self.template.name
#
#     class Meta:
#         verbose_name = _('package node')
#         verbose_name_plural = _('package nodes')
#         unique_together = (
#             ('parent_node', 'template'),
#         )
#
#
# class Validation(BaseModel):
#     """产品验货配置"""
#     name = models.CharField(
#         _('name'),
#         max_length=190,
#         primary_key=True,
#         help_text=_("validation's name")
#     )
#
#     actions = models.ManyToManyField(
#         'django_product.ValidateAction',
#         blank=False,
#         verbose_name=_('validate actions'),
#         help_text=_('the validate action will be used')
#     )
#
#     def __str__(self):
#         return self.name
#
#     class Meta:
#         verbose_name = _('validation')
#         verbose_name_plural = _('validations')
#
#     @property
#     def validators(self):
#         return {action.symbol: action.validator for action in self.actions}
#
#     def is_valid(self, data):
#         """
#         use the validate actions and check the result,if all the action is valid,then return True
#         :param data: dict
#         :return: boolean
#         """
#         validators = self.validators
#         if validators.keys() == data.keys():
#             self.validated_data = {}
#             self.errors = {}
#             is_valid = True
#             for symbol, value in data.items():
#                 validator = validators[symbol]
#                 validator(data={'value': value})
#                 if validator.is_valid():
#                     self.validated_data[symbol] = validator.validated_data['value']
#                 else:
#                     self.errors[symbol] = validator.errors['value']
#                     is_valid = False
#             return is_valid
#         return False
#
#
# class ValidateAction(BaseModel):
#     """产品验货动作"""
#     symbol = models.CharField(
#         _('symbol'),
#         null=False,
#         blank=False,
#         max_length=40,
#         primary_key=True,
#         help_text=_('the symbol of the validator in module')
#     )
#
#     name = models.CharField(
#         _('validator name'),
#         null=False,
#         blank=False,
#         unique=True,
#         max_length=190,
#         help_text=_("validator's more readable name then symbol")
#     )
#
#     uom = ActiveLimitForeignKey(
#         'django_product.UOM',
#         null=False,
#         blank=False,
#         verbose_name=_('uom'),
#         help_text=_('the uom of the check value')
#     )
#
#     explain = models.TextField(
#         _('explain'),
#         null=False,
#         blank=False,
#         help_text=_("validator's explain for usage")
#     )
#
#     def __str__(self):
#         return '{}({})'.format(self.symbol, self.uom)
#
#     class Meta:
#         verbose_name = _('validate action')
#         verbose_name_plural = _('validate actions')
#
#     @property
#     def validator(self):
#         from . import validators
#         if self.symbol in validators.__all__:
#             return getattr(validators, self.symbol, None)
#         return None


# class Barcode(BaseModel):
#     """条形码类"""
#     BARCODE_MODE = (
#         ('Standard39', '标准39'),
#     )
#
#     product = ActiveLimitOneToOneField(
#         'product.Product',
#         null=False,
#         blank=False,
#         verbose_name='产品',
#         help_text="条形码对应的产品"
#     )
#
#     mode = models.CharField(
#         '条形码模式',
#         null=False,
#         blank=False,
#         max_length=20,
#         choices=BARCODE_MODE,
#         help_text="条形码模式"
#     )
#
#     code = models.JSONField(
#         '条形码编码值',
#         null=False,
#         blank=False,
#         json_type='dict',
#         help_text="条形码的编码值字典"
#     )
#
#     have_quiet = models.BooleanField(
#         '是否含有静区',
#         default=False,
#         help_text="条形码是否还有空白区"
#     )
#
#     is_iso_scale = models.BooleanField(
#         '是否被iso收录',
#         default=False,
#         help_text="条形码是否已被iso标准收录"
#     )
#
#     check_sum = models.BooleanField(
#         '是否检查合计',
#         default=False,
#         help_text="条形码是否检查合计"
#     )
