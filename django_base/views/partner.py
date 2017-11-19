#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
@author:    olinex
@time:      2017/11/9 下午9:14
"""

__all__ = ['PartnerViewSet']

from .. import models, serializers, filters
from django_erp.rest.viewsets import BaseViewSet


class PartnerViewSet(BaseViewSet):
    model = models.Partner
    serializer_class = serializers.PartnerSerializer
    filter_class = filters.PartnerFilter