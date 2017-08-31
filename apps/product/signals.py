#!/usr/bin/env python3
# -*- coding:utf-8 -*-

__all__ = ('change_product_template_attribute','create_attribute_md5')

from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver

from . import models
from apps.stock.models import Item


@receiver(m2m_changed, sender=models.ProductTemplate.attributes.through)
def change_product_template_attribute(sender, instance, **kwargs):
    '''
    when relationship between product template and attribute was changed
    '''
    if not kwargs.get('reverse') and kwargs.get('action') in ('post_add', 'post_remove'):
        instance.sync_create_products()
        Item.objects.create(instance=instance)


@receiver(post_save, sender=models.Product)
def create_attribute_md5(sender, instance, created, **kwargs):
    '''
    when product instance was created,calculate the md5 string of the attribute dict json and
    create new products and it's item
    '''
    import json
    from hashlib import md5
    from apps.stock.models import Item
    from django.core.serializers.json import DjangoJSONEncoder
    if not created:
        m = md5()
        m.update(json.dumps(instance.attributes, cls=DjangoJSONEncoder).encode('utf8'))
        instance.attributes_md5 = m.hexdigest()
    else:
        Item.objects.create(instance=instance)
