#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from djangoperm.db import models
from django.conf import settings


class PartnerForeignKey(models.ForeignKey):
    '''合作伙伴外键'''

    def __init__(self, *args, **kwargs):
        kwargs['limit_choices_to'] = kwargs.get('limit_choices_to', {'profile__is_partner': True, 'is_active': True})
        kwargs['on_delete'] = kwargs.get('on_delete', models.PROTECT)
        kwargs['to'] = settings.AUTH_USER_MODEL
        super(PartnerForeignKey, self).__init__(*args, **kwargs)