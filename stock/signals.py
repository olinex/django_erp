#!/usr/bin/env python3
#-*- coding:utf-8 -*-

from . import models
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=models.Zone)
def create_zone_location(sender,instance,**kwargs):
    '''保存时,同步保存库位'''
    models.Location.objects.get_or_create(
        zone=instance,
        parent_location=None,
        is_virtual=True,
        defaults={'x':'','y':'','z':''}
    )