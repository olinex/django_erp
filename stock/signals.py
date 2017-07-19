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
