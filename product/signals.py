#!/usr/bin/env python3
#-*- coding:utf-8 -*-

from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.core.serializers.json import DjangoJSONEncoder
from . import models

@receiver(pre_save, sender=models.Product)
def create_profile(sender, instance, **kwargs):
    '''保存时,更新产品属性的md5值'''
    import json
    from hashlib import md5
    from django.core.serializers.json import DjangoJSONEncoder
    if hasattr(instance,'attributes'):
        m=md5()
        m.update(json.dumps(instance.attributes,cls=DjangoJSONEncoder).encode('utf8'))
        instance.attributes_md5 = m.hexdigest()