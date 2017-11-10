#!/usr/bin/env python3
# -*- coding:utf-8 -*-

__all__ = [
    'create_warehouse_zone',
    'change_route_initial_and_end_setting',
    'get_default_route_for_scrap_order'
]

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction

from . import models


@receiver(post_save, sender=models.Warehouse)
def create_warehouse_zone(sender, instance, created, **kwargs):
    """
    when warehouse instance created,automatically create all zones of
    warehouse and all default routes which are all directly
    """
    if created:
        instance.create_zones_and_routes()


@receiver(post_save, sender=models.RouteSetting)
def change_route_initial_and_end_setting(sender, instance, created, **kwargs):
    """
    when route instance created,automatically create the initial zone setting and end zone setting
    according to the route type
    """
    instance.route.sync_setting_and_type()

@receiver(post_save, sender=models.ScrapOrder)
def get_default_route_for_scrap_order(sender, instance, created, **kwargs):
    """
    when scrap order instance is creating,
    automatically bind the default scrap route
    """
    if not instance.route and instance.location:
        route_type = f'{instance.location.zone}_scrap'
        instance.route = models.Route.get_default_route(
            warehouse=instance.location.warehouse,
            route_type=route_type
        )
        instance.save(update_fields=('route',))
