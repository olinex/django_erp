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

@receiver(post_save, sender=models.RouteLocationSetting)
def sync_initial_and_end_location(sender, instance, **kwargs):
    '''路线的路径库位变化时,同步改变路线的起点库位和终点库位'''
    route = instance.route
    location_settings = models.RouteLocationSetting.objects.filter(route=route)
    initial_location = location_settings.first().location
    end_location = location_settings.last().location
    changed = False
    if route.initial_location != initial_location:
        route.initial_location = initial_location
        changed = True
    if route.end_location != end_location:
        route.end_location = end_location
        changed = True
    if changed:
        route.save(update_fields=('initial_location','end_location'))

