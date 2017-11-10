#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
@author:    olinex
@time:      2017/11/9 下午12:02
"""

__all__ = ['PartnerSerializer']

from django.contrib.auth import get_user_model
from rest_framework import serializers

from django_base.models import Address
from django_base.serializers import AddressSerializer
from common.rest.serializers import ActiveModelSerializer, StatePrimaryKeyRelatedField
from .. import models
from .user import UserSerializer

User = get_user_model()


class PartnerSerializer(ActiveModelSerializer):
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
    address = StatePrimaryKeyRelatedField(Address, 'active')
    default_send_address = StatePrimaryKeyRelatedField(Address, 'active', many=True)
    usual_send_addresses = StatePrimaryKeyRelatedField(Address, 'active', many=True)
    managers = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(is_active=True, is_superuser=False, is_staff=False),
        many=True
    )

    class Meta:
        model = models.Partner
        fields = (
            'id', 'name', 'phone', 'is_active', 'address',
            'default_send_address', 'usual_send_addresses',
            'usual_send_addresses_detail',
            'managers', 'managers_detail',
            'is_company', 'sale_able', 'purchase_able'
        )
