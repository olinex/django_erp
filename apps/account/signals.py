#!/usr/bin/env python3
# -*- coding:utf-8 -*-a

__all__ = ('create_profile',)

from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from . import models

User = get_user_model()


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    '''
    when user instance created,automatically create the profile instance of the user
    '''
    if created:
        models.Profile.objects.create(user=instance)
