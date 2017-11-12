#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
@author:    olinex
@time:      2017/11/9 上午11:53
"""

__all__ = [
    'ProfileSerializer',
    'MailNoticeSerializer',
    'OnlineNoticeSerializer'
]

from rest_framework import serializers

from django_base.models import Address
from .address import AddressSerializer
from .. import models


class ProfileSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    phone = serializers.ReadOnlyField()
    address = AddressSerializer(source='usual_send_addresses', read_only=True)
    mail_notice = serializers.ReadOnlyField()
    online_notice = serializers.ReadOnlyField()

    class Meta:
        model = models.Profile
        fields = (
            'user', 'sex', 'phone', 'language', 'mail_notice', 'online_notice', 'address'
        )


class MailNoticeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Profile
        fields = ('mail_notice',)


class OnlineNoticeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Profile
        fields = ('online_notice',)
