#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
@author:    olinex
@time:      2017/11/9 下午12:02
"""

__all__ = ['PartnerSerializer']

from .. import models
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django_erp.rest.serializers import BaseModelSerializer
from django_erp.rest.fields import StatePrimaryKeyRelatedField

User = get_user_model()


class PartnerSerializer(BaseModelSerializer):

    managers = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(is_active=True, is_superuser=False, is_staff=False),
        many=True
    )

    region = StatePrimaryKeyRelatedField('active', model=models.Region)
    region__name = serializers.CharField(source='region.name', read_only=True)
    region__city = serializers.PrimaryKeyRelatedField(source='region.city', read_only=True)
    region__city__name = serializers.CharField(source='region.city.name', read_only=True)
    region__city__province = serializers.PrimaryKeyRelatedField(source='region.city.province', read_only=True)
    region__city__province__name = serializers.CharField(source='region.city.province.name', read_only=True)

    class Meta:
        model = models.Partner
        fields = '__all__'
