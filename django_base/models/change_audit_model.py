#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
@author:    olinex
@time:      2018/1/20 下午4:46
"""

__all__ = ['ChangeAuditModel']

from . import Change, MessageMachine
from django_perm.db import models
from django.db import transaction
from rest_framework.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.fields import GenericRelation

class ChangeAuditModel(MessageMachine):
    """
    the audit model that will create change when make audit request to
    """
    control_field = []

    changing = models.ForeignKey(
        Change,
        null=True,
        blank=False,
        unique=True,
        verbose_name=_("doing change"),
        help_text=_("the change which is doing")
    )

    def change(self, before, after, creater):
        """
        create the change
        :param before: the dict store the data before change
        :param after: the dict store the data after change
        """
        with transaction.atomic:
            if not self.changing or self.changing.check_states('done','cancelled'):
                changing = Change.objects.create(
                    instance=self, creater=creater, before=before, after=after
                )
                self.changing = changing
                self.save(update_fields=('changing',))
            else:
                ValidationError(_("{} is changing").format(self),code="changing")

    changes = GenericRelation('django_base.Change')

    class Meta:
        abstract = True