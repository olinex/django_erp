#!/usr/bin/env python3
# -*- coding:utf-8 -*-a

from django.db.models.signals import post_save
from django.dispatch import receiver
from . import models
from django.contrib.auth import get_user_model

User = get_user_model()


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    '''每次保存时,检查或创建profile和partner'''
    if created:
        models.Profile.objects.create(user=instance)
