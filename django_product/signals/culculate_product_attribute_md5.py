#!/usr/bin/env python3
# -*- coding:utf-8 -*-

__all__ = ['culculate_product_attribute_md5']

from django.db.models.signals import post_save
from django.dispatch import receiver

from .. import models


@receiver(post_save, sender=models.Product)
def culculate_product_attribute_md5(sender, instance, created, **kwargs):
    """
    when product instance was created,calculate the md5 string of the attribute dict json and
    create new products and it's item
    """
    import json
    from hashlib import md5
    from django.core.serializers.json import DjangoJSONEncoder
    if not created:
        m = md5()
        m.update(json.dumps(instance.attributes, cls=DjangoJSONEncoder, sort_keys=True).encode('utf8'))
        instance.attributes_md5 = m.hexdigest()
