#!/usr/bin/env python3
# -*- coding:utf-8 -*-

__all__ = ('create_warehouse_zone','sync_initial_and_end_zone')

from django.db.models.signals import post_save
from django.dispatch import receiver

from . import models


@receiver(post_save, sender=models.Warehouse)
def create_warehouse_zone(sender, instance, created, **kwargs):
    '''保存时,同步保存仓库的区域'''
    if created:
        instance.create_zones()

@receiver(post_save, sender=models.RouteZoneSetting)
def sync_initial_and_end_zone(sender, instance, **kwargs):
    '''路线的路径库位变化时,同步改变路线的起点库位和终点库位'''
    route = instance.route
    location_settings = models.RouteZoneSetting.objects.filter(route=route)
    initial_zone = location_settings.first().zone
    end_zone = location_settings.last().zone
    changed = False
    if route.initial_zone != initial_zone:
        route.initial_zone = initial_zone
        changed = True
    if route.end_zone != end_zone:
        route.end_zone = end_zone
        changed = True
    if changed:
        route.save(update_fields=('initial_zone','end_zone'))

@receiver(post_save, sender=models.PackageTemplate)
def create_package_template_item(sender,instance,created,**kwargs):
    if created:
        models.Item.objects.create(instance=instance)

