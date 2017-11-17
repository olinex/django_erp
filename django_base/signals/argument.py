#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
@author:    olinex
@time:      2017/11/17 上午9:20
"""

__all__ = ['set_cache','delete_cache']

from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete

from ..models import Argument

@receiver(post_save, sender=Argument)
def set_cache(sender, instance, **kwargs):
    """automatically create the cache data when argument is created"""
    instance.cache.set()

@receiver(post_delete,sender=Argument)
def delete_cache(sender,instance,**kwargs):
    """automatically delete the cache data when arugment is deleted"""
    instance.cache.delete()