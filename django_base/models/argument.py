#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
@author:    olinex
@time:      2017/11/13 下午8:17
"""

__all__ = ['Argument']

import json
from django_perm.db import models
from django_erp.common import Redis
from django_erp.common.models import HistoryModel, SequenceModel
from django.utils.translation import ugettext_lazy as _
from django.core.serializers.json import DjangoJSONEncoder
from rest_framework import serializers
from .message_machine import MessageMachine


class Argument(HistoryModel, SequenceModel):
    class KeyManager(models.Manager):
        def get_by_natural_key(self, name):
            return self.get(name=name)

    objects = KeyManager()

    name = models.CharField(
        _('name'),
        null=False,
        blank=False,
        unique=True,
        max_length=190,
        help_text=_("the name of the argument,it must be unique on the table")
    )

    form = models.CharField(
        _('form'),
        null=False,
        blank=False,
        choices=(
            ('int', _('int')),
            ('str', _('str')),
            ('bool', _('bool')),
            ('list', _('list')),
            ('dict', _('dict'))
        ),
        max_length=10,
        help_text=_("the form of the data")
    )

    value = models.JSONField(
        _('value'),
        form='all',
        help_text=_("the json string value of the argument")
    )

    help_text = models.TextField(
        _('help text'),
        null=True,
        blank=False,
        default=None,
        help_text=_("the help text for user to understand the meaning of the argument")
    )

    class Meta:
        ordering = ['sequence']
        verbose_name = _('argument')
        verbose_name_plural = _('arguments')

    def __str__(self):
        return self.name

    def natural_key(self):
        return (self.name,)

    @staticmethod
    def get_cache(name, instance=None):
        return CacheArgument(
            name=name,
            instance=instance
        )

    @property
    def cache(self):
        return self.get_cache(
            self.name,
            instance=self
        )


class CacheArgument(object):
    """the cache class that comtain the method for redis"""
    PREFIX = 'argument'

    class Serialzier(serializers.ModelSerializer):
        value = serializers.JSONField()
        followers = serializers.JSONField()

        class Meta:
            model = Argument
            fields = '__all__'

    def __init__(self, name, instance=None):
        self.redis = Redis()
        self.name = name
        self.instance = instance

    def __str__(self):
        return self.name

    @property
    def cache_name(self):
        return '{}_{}'.format(self.PREFIX, self.name)

    def get(self):
        value = self.redis.get(self.cache_name)
        if value:
            return json.loads(
                self.redis.get(self.cache_name).decode('utf8')
            )
        else:
            instances = Argument.get_states_queryset(
                'active',
                queryset=Argument.objects.filter(name=self.name)
            )
            if instances.exists():
                self.set(instance=instances.first())
                return self.get()
            return None

    def set(self, instance=None):
        data = self.Serialzier(instance=instance or self.instance).data
        self.redis.set(
            self.cache_name,
            json.dumps(data, cls=DjangoJSONEncoder,sort_keys=True)
        )

    def delete(self):
        self.redis.delete(self.cache_name)
