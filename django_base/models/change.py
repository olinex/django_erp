#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
@author:    olinex
@time:      2018/1/20 下午1:54
"""

__all__ = ['Change']

from django_perm.db import models
from rest_framework import exceptions
from django.utils.translation import ugettext_lazy as _
from django_erp.common.models import OrderModel,ContentTypeModel
from django.contrib.auth import get_user_model

User = get_user_model()

class Change(ContentTypeModel,OrderModel):
    '''the model for audit the request of change'''

    before = models.JSONField(
        _('before value'),
        form='dict',
        default={},
        help_text=_("the json string value of before")
    )

    after = models.JSONField(
        _('after value'),
        form='dict',
        null=False,
        blank=False,
        help_text=_("the json string value of before")
    )

    creater = models.ForeignKey(
        User,
        null=False,
        blank=False,
        verbose_name=_("creater"),
        help_text=_("the creater who create this change")
    )

    class Meta:
        verbose_name = _("change")
        verbose_name_plural = _("change")

    def before_valid(self):
        if not all(
            map(lambda key,value: getattr(self,key) == value,self.before.items())
        ):
            raise exceptions.ValidationError(_("instance was changed"))

    def update_instance(self):
        for key,value in self.after.items():
            setattr(self.instance,key,value)
        self.save(update_fields=self.after.keys())

    def after_do(self, user):
        self.before_valid()
        self.update_instance()
        message = _("change done")
        self.instance.create_message(title=message, text=message, creater=user)

    def after_cancel(self, user):
        message = _("change not allow")
        self.instance.create_message(title=message, text=message, creater=user)







