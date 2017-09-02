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
from .utils import INITIAL_ROUTE_SEQUENCE,END_ROUTE_SEQUENCE


@receiver(post_save, sender=models.Warehouse)
def create_warehouse_zone(sender, instance, created, **kwargs):
    '''
    when warehouse instance created,automatically create all zones of
    warehouse and all default routes which are all directly
    '''
    if created:
        with transaction.atomic():
            instance.create_zones()
            instance.create_default_routes()


@receiver(post_save, sender=models.Route)
def create_initial_and_end_zone_settings(sender, instance, created, **kwargs):
    '''
    when route instance created,automatically create the initial zone setting and end zone setting
    according to the route type
    '''
    if created:
        with transaction.atomic():
            initial = models.RouteSetting(
                name='initial location',
                route=instance,
                loaction=instance.initial_zone.root_location,
                sequence=INITIAL_ROUTE_SEQUENCE
            )
            end = models.RouteSetting(
                name='end location',
                route=instance,
                loaction=instance.end_zone.root_location,
                sequence=END_ROUTE_SEQUENCE
            )
            models.RouteSetting.objects.bulk_create([initial,end])

@receiver(post_save, sender=models.PackageNode)
def create_package_template_item(sender, instance, created, **kwargs):
    '''
    when package node instance created,
    automatically create the stock item instance reflect to the package node
    '''
    if created:
        models.Item.objects.create(instance=instance)

@receiver(post_save, sender=models.ScrapOrder)
def get_default_route_for_scrap_order(sender, instance, created, **kwargs):
    '''
    when scrap order instance is creating,
    automatically bind the default scrap route
    '''
    if not instance.route and instance.location:
        route_type = f'{instance.location.zone.usage}_scrap'
        instance.route = models.Route.get_default_route(
            warehouse=instance.location.zone.warehouse,
            route_type=route_type
        )
        instance.save(update_fields=('route',))
