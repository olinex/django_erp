#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from .utils import QuantityField

from django.db import transaction
from django.db.models import Manager, Q
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django_perm import models
from common.state import Statement, StateMachine
from common.abstractModel import BaseModel, TreeModel
from common.fields import ActiveLimitForeignKey

User = get_user_model()


class PackageType(BaseModel):
    """
    the type of package which define it name,the name must be unique
    """

    name = models.CharField(
        _('name'),
        null=False,
        blank=False,
        unique=True,
        max_length=90,
        help_text=_("the type name of package")
    )

    items = models.ManyToManyField(
        'django_product.Item',
        blank=False,
        through='django_product.PackageTypeSetting',
        through_fields=('package_type', 'item'),
        verbose_name=_('items'),
        help_text=_('the packable items of package')
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('package type')
        verbose_name_plural = _('package types')


class PackageTypeSetting(models.Model, StateMachine):
    """
    Constraint sets the maximum number of packages
    """

    package_type = ActiveLimitForeignKey(
        'django_product.PackageType',
        null=False,
        blank=False,
        verbose_name=_('package type'),
        help_text=_('the type of package which settings belongs to')
    )

    item = ActiveLimitForeignKey(
        'django_product.Item',
        null=False,
        blank=False,
        verbose_name=_('item'),
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
        verbose_name = _('setting of package type')
        verbose_name_plural = _('settings of package type')
        unique_together = (
            ('package_type', 'item'),
        )

    class States:
        product_setting = Statement(
            Q(item__content_type__app_label='django_product') &
            Q(item__content_type__model='Product')
        )


class PackageTemplate(BaseModel):
    """
    the template of package type
    """

    name = models.CharField(
        _('name'),
        null=False,
        blank=False,
        unique=True,
        max_length=90,
        help_text=_('the name of package template')
    )

    package_type = ActiveLimitForeignKey(
        'django_product.PackageType',
        null=False,
        blank=False,
        verbose_name=_('package type'),
        help_text=_('the package type of this template,constraint max number of item')
    )

    type_settings = models.ManyToManyField(
        'django_product.PackageTypeSetting',
        blank=False,
        through='django_product.PackageTemplateSetting',
        through_fields=('package_template', 'type_setting'),
        verbose_name=_('the type settings of package'),
        help_text=_('the type settings of package which constraint max number of item')
    )

    def __str__(self):
        return str(self.package_type)

    class Meta:
        verbose_name = _('package template')
        verbose_name_plural = _('package templates')


class PackageTemplateSetting(models.Model):
    """
    the setting which set the number of item in the package
    """

    package_template = ActiveLimitForeignKey(
        'django_product.PackageTemplate',
        null=False,
        blank=False,
        verbose_name=_('package template'),
        help_text=_('the package template which setting belongs to')
    )

    type_setting = models.ForeignKey(
        'django_product.PackageTypeSetting',
        null=False,
        blank=False,
        verbose_name=_('package type setting'),
        help_text=_('the package type setting will constraint the max number of item of this template setting')
    )

    quantity = QuantityField(
        _('quantity'),
        null=False,
        blank=False,
        uom='type_setting.uom',
        validators=[MinValueValidator(0)],
        help_text=_('the quantity of item in package template')
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


class PackageNode(TreeModel, StateMachine):
    """
    package node,every node contain an package template
    """

    template = ActiveLimitForeignKey(
        'django_product.PackageTemplate',
        null=False,
        blank=False,
        verbose_name=_('package template'),
        help_text=_('package template in the package tree')
    )

    quantity = models.PositiveSmallIntegerField(
        _('quantity'),
        null=False,
        blank=False,
        help_text=_('the quantity of the template in this node')
    )

    items = GenericRelation('django_product.Item')

    @property
    def item(self):
        if not hasattr(self, '__item'):
            self.__item = self.items.first()
        return self.__item

    @property
    def child_quantity_dict(self):
        """
        return the dict of all childs pk and quantity dict,
        and an empty string with itself's quantity
        :return: dict
        """
        result = dict(self.all_child_nodes.values_list('pk', 'quantity'))
        return result

    def __str__(self):
        return self.template.name

    class Meta:
        verbose_name = _('package node')
        verbose_name_plural = _('package nodes')
        unique_together = (
            ('parent_node', 'template'),
        )



class ProductCategory(BaseModel):
    """product category"""
    name = models.CharField(
        _('name'),
        primary_key=True,
        max_length=90,
        help_text=_('the name of product category')
    )

    sequence = models.PositiveIntegerField(
        _('sequence'),
        null=False,
        blank=True,
        default=0,
        help_text=_('the order of the product category')
    )

    class Meta:
        verbose_name = _('product category')
        verbose_name_plural = _('product categories')
        ordering = ('sequence',)

    def __str__(self):
        return self.name


class Product(BaseModel):
    """产品"""
    template = ActiveLimitForeignKey(
        'django_product.ProductTemplate',
        null=False,
        blank=False,
        on_delete=models.PROTECT,
        verbose_name=_('product template'),
        help_text=_('the template of the product')
    )

    attributes = models.JSONField(
        _('attributes'),
        null=False,
        blank=False,
        default={},
        json_type='dict',
        help_text=_('the json value of the attributes dict')
    )

    prices = models.JSONField(
        _('prices'),
        null=False,
        blank=False,
        default={},
        json_type='dict',
        help_text=_('the json value of the flow over price dict')
    )

    attributes_md5 = models.CharField(
        _('attributes md5'),
        null=False,
        blank=False,
        max_length=40,
        help_text=_('the value of attribute dict json md5,for unique require')
    )

    in_code = models.CharField(
        _('inner code'),
        null=True,
        blank=False,
        max_length=190,
        help_text=_('the inner code of product for private using')
    )

    out_code = models.CharField(
        _('outer code'),
        null=True,
        blank=False,
        max_length=190,
        help_text=_('the outer code of product for public using')
    )

    weight = models.DecimalField(
        _('weight'),
        null=False,
        blank=True,
        max_digits=24,
        decimal_places=12,
        default=0,
        help_text=_("product's weight,uom is kg")
    )

    volume = models.DecimalField(
        _('volume'),
        null=False,
        blank=True,
        max_digits=24,
        decimal_places=12,
        default=0,
        help_text=_("product's volume,uom is m3")
    )

    salable = models.BooleanField(
        _('sale status'),
        null=False,
        blank=True,
        default=False,
        help_text=_('True means product can be sale')
    )

    purchasable = models.BooleanField(
        _('purchase status'),
        null=False,
        blank=True,
        default=False,
        help_text=_('True means product can be purchased')
    )

    rentable = models.BooleanField(
        _('rent status'),
        null=False,
        blank=True,
        default=False,
        help_text=_('True means product can be rented')
    )

    items = GenericRelation('django_product.Item')

    @property
    def item(self):
        """
        get the relate item about itself,in the product.Item,it constraint the ccontent type and instance id,
        so it must have the only one item
        :return: product.Item instance
        """
        if not hasattr(self, '__item'):
            self.__item = self.items.first()
        return self.__item

    @property
    def uom(self):
        return self.template.uom

    def __str__(self):
        return '{}({})'.format(self.template.name,self.attributes_str)

    class Meta:
        verbose_name = _('product')
        verbose_name_plural = _('products')
        unique_together = ('template', 'attributes_md5')

    @property
    def attributes_str(self):
        return '/'.join(
            [
                '{}:{}'.format(key, value)
                for key, value in self.attributes.items()
            ]
        )


class Validation(BaseModel):
    """产品验货配置"""
    name = models.CharField(
        _('name'),
        max_length=190,
        primary_key=True,
        help_text=_("validation's name")
    )

    actions = models.ManyToManyField(
        'django_product.ValidateAction',
        blank=False,
        verbose_name=_('validate actions'),
        help_text=_('the validate action will be used')
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('validation')
        verbose_name_plural = _('validations')

    @property
    def validators(self):
        return {action.symbol: action.validator for action in self.actions}

    def is_valid(self, data):
        """
        use the validate actions and check the result,if all the action is valid,then return True
        :param data: dict
        :return: boolean
        """
        validators = self.validators
        if validators.keys() == data.keys():
            self.validated_data = {}
            self.errors = {}
            is_valid = True
            for symbol, value in data.items():
                validator = validators[symbol]
                validator(data={'value': value})
                if validator.is_valid():
                    self.validated_data[symbol] = validator.validated_data['value']
                else:
                    self.errors[symbol] = validator.errors['value']
                    is_valid = False
            return is_valid
        return False


class ValidateAction(BaseModel):
    """产品验货动作"""
    symbol = models.CharField(
        _('symbol'),
        null=False,
        blank=False,
        max_length=40,
        primary_key=True,
        help_text=_('the symbol of the validator in module')
    )

    name = models.CharField(
        _('validator name'),
        null=False,
        blank=False,
        unique=True,
        max_length=190,
        help_text=_("validator's more readable name then symbol")
    )

    uom = ActiveLimitForeignKey(
        'django_product.UOM',
        null=False,
        blank=False,
        verbose_name=_('uom'),
        help_text=_('the uom of the check value')
    )

    explain = models.TextField(
        _('explain'),
        null=False,
        blank=False,
        help_text=_("validator's explain for usage")
    )

    def __str__(self):
        return '{}({})'.format(self.symbol, self.uom)

    class Meta:
        verbose_name = _('validate action')
        verbose_name_plural = _('validate actions')

    @property
    def validator(self):
        from . import validators
        if self.symbol in validators.__all__:
            return getattr(validators, self.symbol, None)
        return None


class ProductTemplate(BaseModel):
    """product template"""
    STOCK_TYPE = (
        ('service', _('service')),
        ('digital', _('digital')),
        ('stock-expiration', _('stock expiration')),
        ('stock-no-expiration', _('stock not expiration')),
        ('consumable', _('consumable product'))
    )
    name = models.CharField(
        _('name'),
        unique=True,
        null=False,
        blank=False,
        max_length=190,
        help_text=_("product template's name")
    )

    stock_type = models.CharField(
        _('stock type'),
        null=False,
        blank=False,
        max_length=20,
        choices=STOCK_TYPE,
        help_text=_('the type of product how to stock')
    )

    attributes = models.ManyToManyField(
        'django_product.Attribute',
        verbose_name=_('attributes'),
        help_text=_('the attributes and product relationship')
    )

    uom = ActiveLimitForeignKey(
        'django_product.UOM',
        null=False,
        blank=False,
        verbose_name=_('uom'),
        on_delete=models.PROTECT,
        help_text=_("product's unit of measurement")
    )

    sequence = models.PositiveIntegerField(
        _('sequence'),
        null=False,
        blank=True,
        default=0,
        help_text=_('the order of product template')
    )

    detail = models.CharField(
        _('detail'),
        null=False,
        blank=True,
        default='',
        max_length=190,
        help_text=_('the detail message of product template')
    )

    in_description = models.TextField(
        _('inner description'),
        null=False,
        blank=True,
        default='',
        help_text=_('the description of product template for private using')
    )

    out_description = models.TextField(
        _('outer description'),
        null=False,
        blank=True,
        default='',
        help_text=_('the description of product template for public using')
    )

    category = ActiveLimitForeignKey(
        'django_product.ProductCategory',
        null=True,
        blank=True,
        verbose_name=_('product category'),
        help_text=_('the category of product')
    )

    validation = ActiveLimitForeignKey(
        'django_product.Validation',
        null=True,
        blank=False,
        verbose_name=_('validation'),
        help_text=_('the validation will be checked in check order')
    )

    class Meta:
        verbose_name = _('product template')
        verbose_name_plural = _('product templates')

    def __str__(self):
        return self.name

    @property
    def attribute_combination(self):
        from itertools import product
        attributes = self.attributes.all().values_list('name', 'value', 'extra_price')
        key_list = [attr[0] for attr in attributes]
        attribute_value = [zip(*attr[1:]) for attr in attributes]
        for value_tuple in product(*attribute_value):
            yield dict(zip(key_list, value_tuple))

    def sync_create_products(self):
        from common.utils import md5_hexdigest
        with transaction.atomic():
            for attributes in self.attribute_combination:
                value_dict = {attr: value[0] for attr, value in attributes.items()}
                price_dict = {attr: value[1] for attr, value in attributes.items()}
                Product.objects.get_or_create(
                    template=self,
                    attributes_md5=md5_hexdigest(value_dict),
                    defaults={
                        'attributes': value_dict,
                        'prices': price_dict,
                        'is_active': False
                    }
                )


class Attribute(BaseModel):
    """属性"""
    name = models.CharField(
        _('attribute name'),
        null=False,
        blank=False,
        unique=True,
        max_length=190,
        help_text=_('the name of product attribute')
    )

    value = models.JSONField(
        _('value'),
        null=False,
        blank=False,
        json_type='list',
        help_text=_('json list of value for attribute')
    )

    extra_price = models.JSONField(
        _('extra price'),
        null=False,
        blank=False,
        json_type='list',
        help_text=_('json list of price for attribute')
    )

    class Meta:
        verbose_name = _('attribute')
        verbose_name_plural = _('attributes')

    def __str__(self):
        return self.name

    @property
    def value_price_tuple(self):
        return zip(
            self.value,
            self.extra_price
        )


class UOM(BaseModel):
    """计量单位"""

    class KeyManager(Manager):
        def get_by_natural_key(self, symbol):
            return self.get(symbol=symbol)

    objects = KeyManager()

    UOM_CATEGORY = (
        ('m',       _('meter')),
        ('kg',      _('kilogram')),
        ('s',       _('second')),
        ('A',       _('Ampere')),
        ('K',       _('Kelvins')),
        ('J',       _('Joule')),
        ('m2',      _('square meter')),
        ('m3',      _('cubic meter')),
        ('unit',    _('unit')),
        ('yuan',    _('yuan'))
    )

    ROUND_METHOD = (
        ('ROUND_CEILING',   _('round ceiling')),            #趋向无穷取整
        ('ROUND_DOWN',      _('round down')),               #趋向0取整
        ('ROUND_FLOOR',     _('round floor')),              #趋向负无穷取整
        ('ROUND_HALF_DOWN', _('round half down')),          #末位大于五反向零取整,否则趋向零取整
        ('ROUND_HALF_EVEN', _('round half even')),          #末位大于五反向零取整,小于五趋向零取整,遇五前位为奇数反向零取整
        ('ROUND_HALF_UP',   _('round half up')),            #末位大于等于五反向零取整,否则趋向零取整
        ('ROUND_UP',        _('round up')),                 #反向0取整
        ('ROUND_05UP',      _('round zero and half up'))    #取整位数为零或五时反向零取整,否则趋向零取整
    )

    name = models.CharField(
        _('name'),
        null=False,
        blank=False,
        max_length=20,
        unique=True,
        help_text=_("the verbose of the uom")
    )

    symbol = models.CharField(
        _('symbol'),
        null=False,
        blank=False,
        unique=True,
        max_length=10,
        help_text=_("the symbol of the uom in math")
    )

    decimal_places = models.PositiveSmallIntegerField(
        _('decimal places'),
        null=False,
        blank=False,
        default=3,
        help_text=_('the decimal places of the uom value')
    )

    round_method = models.CharField(
        _('round method'),
        null=False,
        blank=False,
        max_length=20,
        choices=ROUND_METHOD,
        default='ROUND_CEILING',
        help_text=_("the method will be used when the value of uom was rounding")
    )

    ratio = models.DecimalField(
        _('ratio'),
        max_digits=24,
        decimal_places=12,
        null=False,
        blank=False,
        help_text=_("""
        the ratio of the uom compare with standard unit,when ratio is bigger than 1,
        means uom is greater than standard unit
        """)
    )

    category = models.CharField(
        _('category'),
        null=False,
        blank=False,
        max_length=10,
        choices=UOM_CATEGORY,
        help_text=_("""
        the category of the uom,uom value can be converted to other uom value only when their in the same category
        """)
    )

    @property
    def ratio_type(self):
        if self.ratio > 1:
            return _('bigger')
        if self.ratio == 1:
            return _('equal')
        if 0 < self.ratio < 1:
            return _('smaller')

    class Meta:
        verbose_name = _('uom')
        verbose_name_plural = _('uoms')

    def __str__(self):
        return '{}({})'.format(self.name,self.symbol)

    def natural_key(self):
        return (self.symbol,)

    def accuracy_convert(self, value):
        """
        convert value's precision to this uom's precision
        :param value: decimal
        :return: decimal
        """
        import decimal
        with decimal.localcontext() as ctx:
            ctx.prec = 24
            return value.quantize(
                decimal.Decimal('0.' + ('0' * self.decimal_places)),
                rounding=getattr(decimal, self.round_method),
            )

    def convert(self, value, to_uom):
        """
        convert value as this uom precision and ratio to another uom
        :param value: decimal
        :param to_uom: uom
        :return: decimal
        """
        if self.category == to_uom.category:
            new_value = value * self.ratio / to_uom.ratio
            return to_uom.accuracy_convert(new_value)
        raise AttributeError(_('uom can not be convert to other uom until their category is the same'))


class Lot(BaseModel):
    """lot number"""
    name = models.CharField(
        _('name'),
        null=False,
        blank=False,
        unique=True,
        max_length=90,
        help_text=_('the name of lot')
    )

    product = ActiveLimitForeignKey(
        'django_product.Product',
        null=False,
        blank=False,
        verbose_name=_('product'),
        help_text=_('the product of the lot')
    )

    class Meta:
        verbose_name = _('lot')
        verbose_name_plural = _('lots')

    def __str__(self):
        return self.name


class Item(BaseModel):
        """
        stock item is project what can be stock and move
        """

        content_type = models.ForeignKey(
            ContentType,
            null=False,
            blank=False,
            verbose_name=_('content type'),
            help_text=_('the type of content reflect to the model')
        )

        object_id = models.PositiveIntegerField(
            _('item id'),
            null=False,
            blank=False,
            help_text=_('the primary key for the project')
        )

        instance = GenericForeignKey('content_type', 'object_id')

        def __str__(self):
            return str(self.instance)

        class Meta:
            verbose_name = _('stock item')
            verbose_name_plural = _('stock items')
            unique_together = ('content_type', 'object_id')

        class States(BaseModel.States):
            active = BaseModel.States.active
            product = Statement(
                Q(content_type__app_label='django_product') & Q(content_type__model='product'),
                inherits=active
            )
            package_node = Statement(
                Q(content_type__app_label='django_product') & Q(content_type__model='packagenode'),
                inherits=active
            )


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
