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
    '''
    when warehouse instance created,automatically create all zones of
    warehouse and all default routes which are all directly
    '''
    if created:
        instance.create_zones()
        instance.create_default_routes()


@receiver(post_save, sender=models.Route)
def create_initial_and_end_zone_settings(sender, instance, created, **kwargs):
    '''
    when route instance created,automatically create the initial zone setting and end zone setting
    according to the route type
    '''
    if created:
        initial = models.RouteZoneSetting(
            name='initial zone',
            route=instance,
            zone=instance.initial_zone,
            sequence=0
        )
        end = models.RouteZoneSetting(
            name='end zone',
            route=instance,
            zone=instance.end_zone,
            sequence=32767
        )
        models.RouteZoneSetting.objects.bulk_create([initial,end])

@receiver(post_save, sender=models.PackageNode)
def create_package_template_item(sender, instance, created, **kwargs):
    '''
    when package node instance created,
    automatically create the stock item instance reflect to the package node
    '''
    if created:
        models.Item.objects.create(instance=instance)
