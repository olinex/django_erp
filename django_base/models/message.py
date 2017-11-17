#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
@author:    olinex
@time:      2017/11/14 下午7:15
"""

from django_perm.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

User = get_user_model()


class Message(models.Model):
    """
    for all the model to log theirs action message
    """
    creater = models.ForeignKey(
        User,
        null=False,
        blank=False,
        db_constraint=False,
        related_name='create_message_set',
        verbose_name=_('create user'),
        help_text=_("the user who create the message")
    )

    create_time = models.DateTimeField(
        _('create time'),
        null=False,
        blank=False,
        auto_now_add=True,
        help_text=_('will auto write when create this node')
    )

    title = models.CharField(
        _('title'),
        null=False,
        blank=False,
        max_length=64,
        help_text=_("the title of the message")
    )

    text = models.TextField(
        _('text'),
        null=False,
        blank=False,
        help_text=_("the text of the action message")
    )

    content_type = models.ForeignKey(
        ContentType,
        null=False,
        blank=False,
        verbose_name=_('content type'),
        help_text=_('the type of content reflect to the model')
    )

    object_id = models.PositiveIntegerField(
        _('item id'),
        null=False,
        blank=False,
        help_text=_('the primary key for the project')
    )

    instance = GenericForeignKey('content_type', 'object_id')

    class Meta:
        verbose_name = _('message')
        verbose_name_plural = _('message')
