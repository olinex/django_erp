#!/usr/bin/env python3
#-*- coding:utf-8 -*-

from common.abstractModel import BaseModel
from common.fields import ActiveLimitForeignKey
from apps.djangoperm.db import models

# Create your models here.

class Rule(BaseModel):
    '''生产规则'''
    template = ActiveLimitForeignKey(
        'product.ProductTemplate',
        null=False,
        blank=False,

    )
