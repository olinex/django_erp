#!/usr/bin/env python3
#-*- coding:utf-8 -*-

from django.utils.translation import ugettext_lazy as _

from common.abstractModel import BaseModel
from common.fields import ActiveLimitForeignKey,ActiveLimitOneToOneField
from apps.djangoperm.db import models

# Create your models here.

class BOM(BaseModel):
    '''
    bill of manufacture
    '''
    product = ActiveLimitOneToOneField(
        'product.Product',
        null=False,
        blank=False,
        verbose_name=_('the product for produce'),
        help_text=_('the product output from production')
    )


