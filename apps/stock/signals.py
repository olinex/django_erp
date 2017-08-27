#!/usr/bin/env python3
# -*- coding:utf-8 -*-

__all__ = (
    'create_warehouse_zone',
    'create_initial_and_end_zone_settings',
    'create_package_template_item'
)

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction

from . import models


@receiver(post_save, sender=models.Warehouse)
def create_warehouse_zone(sender, instance, created, **kwargs):
    '''创建时,同步保存仓库的区域'''
    if created:
        instance.create_zones()
        instance.create_default_routes()


@receiver(post_save, sender=models.Route)
def create_initial_and_end_zone_settings(sender, instance, created, **kwargs):
    if created:
        initial = models.RouteZoneSetting(
            route=instance,
            zone=instance.initial_zone,
            sequence=0
        )
        end = models.RouteZoneSetting(
            route=instance,
            zone=instance.end_zone,
            sequence=32767
        )
        models.RouteZoneSetting.objects.bulk_create([initial,end])
    else:
        with transaction.atomic():
            settings = models.RouteZoneSetting.objects.filter(route=instance)
            initial_zone = instance.initial_zone
            end_zone = instance.end_zone
            initial_setting = settings.first()
            end_setting = settings.last()
            if initial_zone != initial_setting.zone:
                initial_setting.update(zone=initial_zone)
            if end_zone != end_setting.zone:
                end_setting.update(zone=end_zone)


@receiver(post_save, sender=models.PackageNode)
def create_package_template_item(sender, instance, created, **kwargs):
    if created:
        models.Item.objects.create(instance=instance)
