#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from django.conf import settings
from django.db.models import Manager

from apps.djangoperm import models
from common.abstractModel import BaseModel
from common.fields import ActiveLimitForeignKey, ActiveLimitOneToOneField, ActiveLimitManyToManyField

COUNTRIES = (
    ('China', '中国'),
)


class Province(models.Model):
    '''省份'''

    class KeyManager(Manager):
        def get_by_natural_key(self, country, name):
            return self.get(country=country, name=name)

    objects = KeyManager()

    country = models.CharField(
        '国家',
        null=False,
        blank=False,
        choices=COUNTRIES,
        max_length=90,
        help_text="省份的所属国家"
    )

    name = models.CharField(
        '名称',
        null=False,
        blank=False,
        max_length=90,
        help_text="省份的名称"
    )

    class Meta:
        verbose_name = '省份'
        verbose_name_plural = '省份'
        unique_together = ('country', 'name')

    def __str__(self):
        return self.get_country_display() + '/' + self.name

    def natural_key(self):
        return (self.country, self.name)


class City(models.Model):
    '''城市'''
    class KeyManager(Manager):
        def get_by_natural_key(self,country,province,name):
            return self.get(
                province__country=country,
                province__name=province,
                name=name
            )

    objects = KeyManager()

    province = models.ForeignKey(
        'account.Province',
        null=False,
        blank=False,
        related_name='cities',
        verbose_name='省份',
        help_text="城市的所属省份"
    )

    name = models.CharField(
        '名称',
        null=False,
        blank=False,
        max_length=90,
        help_text="城市的名称"
    )

    class Meta:
        verbose_name = '城市'
        verbose_name_plural = '城市'
        unique_together = ('province', 'name')

    def __str__(self):
        return str(self.province) + '/' + self.name

    def natural_key(self):
        return self.province.natural_key() + (self.name,)
    natural_key.dependencies = ['account.Province']


class Region(models.Model):
    '''地区'''
    city = models.ForeignKey(
        'account.City',
        null=False,
        blank=False,
        related_name='regions',
        verbose_name='城市',
        help_text="地区的所属城市"
    )

    name = models.CharField(
        '名称',
        null=False,
        blank=False,
        max_length=90,
        help_text="地区的名称"
    )

    class Meta:
        verbose_name = '地区'
        verbose_name_plural = '地区'
        unique_together = ('city', 'name')

    def __str__(self):
        return str(self.city) + '/' + self.name


class Address(BaseModel):
    '''顾客或公司的地址'''
    region = models.ForeignKey(
        'account.Region',
        null=False,
        blank=False,
        related_name='addresses',
        verbose_name='地区',
        help_text="地址的所属地区"
    )

    name = models.CharField(
        '地址名称',
        null=False,
        blank=False,
        max_length=190,
        help_text="特定地址的名称"
    )

    class Meta:
        verbose_name = '地址'
        verbose_name_plural = '地址'
        unique_together = ('region', 'name')

    def __str__(self):
        return str(self.region) + '/' + self.name


class Profile(models.Model):
    '''用户的其他信息'''
    SEX_CHOICES = (
        ('unknown', '未知'),
        ('male', '男'),
        ('female', '女'),
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        primary_key=True,
        verbose_name='绑定用户',
        help_text='一对一绑定的相关django内置用户')

    sex = models.CharField(
        '性别',
        null=False,
        default='unknown',
        max_length=10,
        choices=SEX_CHOICES,
        help_text="用户的性别"
    )

    phone = models.CharField(
        "移动电话",
        max_length=11,
        null=True,
        blank=False,
        unique=True,
        default=None,
        help_text="用户唯一的移动电话"
    )

    language = models.CharField(
        '语言',
        null=True,
        blank=False,
        default='zh-han',
        max_length=20,
        choices=settings.LANGUAGES,
        help_text="用户设置的默认语言"
    )

    address = ActiveLimitOneToOneField(
        'account.Address',
        null=True,
        blank=True,
        help_text='合作伙伴的所在地址'
    )

    default_send_address = ActiveLimitForeignKey(
        'account.Address',
        null=True,
        blank=True,
        related_name='default_profiles',
        verbose_name='默认地址',
        help_text="合作伙伴设置的默认送货地址"
    )

    usual_send_addresses = ActiveLimitManyToManyField(
        'account.Address',
        blank=True,
        related_name='usual_profiles',
        verbose_name='常用地址',
        help_text="合作伙伴的常用送货地址"
    )

    mail_notice = models.BooleanField(
        '邮件提醒',
        default=True,
        help_text="站内邮件提醒状态,为True时,实时提醒用户有未读的新邮件"
    )

    online_notice = models.BooleanField(
        '在线提醒',
        default=False,
        help_text="在线提醒状态,为True时,其他用户可以接收该用户的在线状态,并告知其下线"
    )

    salable = models.BooleanField(
        '可销售状态',
        default=True,
        help_text="合作伙伴是否可被销售货物"
    )

    purchasable = models.BooleanField(
        '可采购状态',
        default=False,
        help_text="是否可向合作伙伴采购"
    )

    is_partner = models.BooleanField(
        '是否为合作伙伴',
        default=False,
        help_text="表示用户是否为合作伙伴"
    )

    class Meta:
        verbose_name = '用户其他资料'
        verbose_name_plural = '用户其他资料'

    def __str__(self):
        return '{}-{}'.format(self.user.id, self.user.get_full_name() or self.user.get_username())


class Company(BaseModel):
    '''公司'''
    name = models.CharField(
        '名称',
        null=False,
        blank=False,
        max_length=90,
        help_text="公司的名称",
    )

    tel = models.CharField(
        '电话',
        null=False,
        blank=False,
        default='',
        max_length=32,
        help_text='公司电话')

    address = ActiveLimitOneToOneField(
        'account.Address',
        verbose_name='公司地址',
        null=True,
        blank=True,
        help_text='公司的所在地址,必须为公司对应合作伙伴的常用送货地址')

    default_send_address = ActiveLimitForeignKey(
        'account.Address',
        null=True,
        blank=True,
        related_name='default_companies',
        verbose_name='默认送货地址',
        help_text="公司设置的默认送货地址"
    )

    usual_send_addresses = ActiveLimitManyToManyField(
        'account.Address',
        related_name='usual_companies',
        verbose_name='常用送货地址',
        help_text="公司的常用送货地址"
    )

    belong_users = ActiveLimitManyToManyField(
        settings.AUTH_USER_MODEL,
        verbose_name='公司管理员',
        related_name='belong_companies',
        limit_choices_to={'is_active': True, 'is_superuser': False, 'is_staff': False},
        help_text='管理公司的人员')

    salable = models.BooleanField(
        '可销售状态',
        default=True,
        help_text="公司是否可被销售货物"
    )

    purchasable = models.BooleanField(
        '可采购状态',
        default=False,
        help_text="是否可向公司采购"
    )

    class Meta:
        verbose_name = '公司'
        verbose_name_plural = '公司'
        unique_together = ('name', 'address')

    def __str__(self):
        return self.name
