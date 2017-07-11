#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from . import models
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver


@receiver(post_save, sender=models.Warehouse)
def create_warehouse_zone(sender, instance, created, **kwargs):
    '''保存时,同步保存仓库的区域'''
    if created:
        instance.create_zones()


@receiver(post_save, sender=models.Zone)
def create_zone_location(sender, instance, created, **kwargs):
    '''保存时,同步保存库位'''
    if created:
        models.Location.objects.create(
            zone=instance,
            parent_node=None,
            is_virtual=True,
            x='', y='', z=''
        )


@receiver(pre_save, sender=models.Route)
def create_map_md5(sender, instance, **kwargs):
    '''保存时,更新路径列表的md5值'''
    import json
    from hashlib import md5
    from django.core.serializers.json import DjangoJSONEncoder
    if hasattr(instance, 'map'):
        m = md5()
        m.update(json.dumps(instance.map, cls=DjangoJSONEncoder).encode('utf8'))
        instance.map_md5 = m.hexdigest()
