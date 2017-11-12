#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
@author:    olinex
@time:      2017/11/9 下午12:02
"""

__all__ = ['PartnerSerializer']

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .address import AddressSerializer
from django_erp.rest.serializers import BaseModelSerializer
from .. import models
from .user import UserSerializer

User = get_user_model()


class PartnerSerializer(BaseModelSerializer):
    usual_send_addresses_detail = AddressSerializer(
        source='usual_send_addresses',
        read_only=True,
        many=True
    )
    managers_detail = UserSerializer(
        source='managers',
        read_only=True,
        many=True
    )

    managers = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(is_active=True, is_superuser=False, is_staff=False),
        many=True
    )

    class Meta:
        model = models.Partner
        fields = '__all__'
