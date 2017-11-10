#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
@author:    olinex
@time:      2017/11/9 下午9:14
"""

__all__ = ['PartnerViewSet']

from common.rest.viewsets import BaseViewSet
from .. import models
from .. import serializers


class PartnerViewSet(BaseViewSet):
    model = models.Partner
    serializer_class = serializers.PartnerSerializer
