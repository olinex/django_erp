#!/usr/bin/env python3
#-*- coding:utf-8 -*-

from djangoperm.db import models
from django.conf import settings
from django.core.urlresolvers import reverse
from common.abstractModel import BaseModel

COUNTRYS = (
    ('China','中国'),
)

class Province(BaseModel):
    '''省份'''
    country = models.CharField(
        '国家',
        null=False,
        blank=False,
        choices=COUNTRYS,
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
        unique_together=('country','name')

    def __str__(self):
        return self.get_country_display() + '/' + self.name

class City(BaseModel):
    '''城市'''
    province = models.ForeignKey(
        Province,
        null=False,
        blank=False,
        related_name='cities',
        verbose_name='省份',
        help_text="城市的所属省份"
    )

    name =  models.CharField(
        '名称',
        null=False,
        blank=False,
        max_length=90,
        help_text="城市的名称"
    )

    class Meta:
        verbose_name = '城市'
        verbose_name_plural = '城市'
        unique_together=('province','name')

    def __str__(self):
        return str(self.province) + '/' + self.name

class Region(BaseModel):
    '''地区'''
    city = models.ForeignKey(
        City,
        null=False,
        blank=False,
        related_name='regions',
        verbose_name='城市',
        help_text="地区的所属城市"
    )

    name =  models.CharField(
        '名称',
        null=False,
        blank=False,
        max_length=90,
        help_text="地区的名称"
    )

    class Meta:
        verbose_name = '地区'
        verbose_name_plural = '地区'
        unique_together=('city','name')

    def __str__(self):
        return str(self.city) + '/' + self.name

class Address(BaseModel):
    '''顾客或公司的地址'''
    region = models.ForeignKey(
        Region,
        null=False,
        blank=False,
        related_name='addresses',
        verbose_name='地区',
        help_text="地址的所属地区"
    )

    name = models.TextField(
        '地址名称',
        null=False,
        blank=False,
        help_text="特定地址的名称"
    )

    class Meta:
        verbose_name = '地址'
        verbose_name_plural = '地址'

    def __str__(self):
        return str(self.region)+'/'+self.name

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

    mail_notice = models.BooleanField(
        '邮件提醒',
        default=True,
        help_text="站内邮件提醒状态,为True时,实时提醒用户有未读的新邮件"
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

    online_notice = models.BooleanField(
        '在线提醒',
        default=False,
        help_text="在线提醒状态,为True时,其他用户可以接收该用户的在线状态,并告知其下线"
    )

    class Meta:
        verbose_name = '用户其他资料'
        verbose_name_plural = '用户其他资料'

    def __str__(self):
        return '{}-{}'.format(self.user.id, self.user.get_full_name() or self.user.get_username())

class Partner(BaseModel):
    '''合作伙伴'''
    name = models.CharField(
        '名称',
        null=False,
        blank=False,
        unique=True,
        max_length=90,
        help_text="合作伙伴的名称",
    )

    tel = models.CharField(
        '电话',
        null=False,
        blank=False,
        default='',
        max_length=32,
        help_text='合作伙伴电话'
    )

    address = models.OneToOneField(
        Address,
        null=True,
        blank=True,
        help_text='合作伙伴的所在地址'
    )

    default_send_address = models.ForeignKey(
        Address,
        null=True,
        blank=True,
        related_name='default_partners',
        verbose_name='默认地址',
        help_text="合作伙伴设置的默认送货地址"
    )

    usual_send_addresses = models.ManyToManyField(
        Address,
        related_name='usual_partners',
        verbose_name='常用地址',
        help_text="合作伙伴的常用送货地址"
    )

    can_sale = models.BooleanField(
        '可销售状态',
        default=True,
        help_text="合作伙伴是否可被销售货物"
    )

    can_purchase = models.BooleanField(
        '可采购状态',
        default=False,
        help_text="是否可向合作伙伴采购"
    )

    class Meta:
        verbose_name = '合作伙伴'
        verbose_name_plural = '合作伙伴'
        unique_together=('name','address')


    def __str__(self):
        return self.name

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

    address = models.OneToOneField(
        Address,
        verbose_name='公司地址',
        null=True,
        blank=True,
        help_text='公司的所在地址,必须为公司对应合作伙伴的常用送货地址')

    default_send_address = models.ForeignKey(
        Address,
        null=True,
        blank=True,
        related_name='default_companies',
        verbose_name='默认送货地址',
        help_text="公司设置的默认送货地址"
    )

    usual_send_addresses = models.ManyToManyField(
        Address,
        related_name='usual_companies',
        verbose_name='常用送货地址',
        help_text="公司的常用送货地址"
    )

    belong_customers = models.ManyToManyField(
        Partner,
        verbose_name='公司管理员',
        related_name='belong_companies',
        help_text='管理公司的人员')

    can_sale = models.BooleanField(
        '可销售状态',
        default=True,
        help_text="公司是否可被销售货物"
    )

    can_purchase = models.BooleanField(
        '可采购状态',
        default=False,
        help_text="是否可向公司采购"
    )

    class Meta:
        verbose_name = '公司'
        verbose_name_plural = '公司'
        unique_together=('name','address')

    def __str__(self):
        return self.name

