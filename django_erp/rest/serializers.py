#!/usr/bin/env python3
# -*- coding:utf-8 -*-

__all__ = [
    'BaseModelSerializer',
    'DataModelSerializer',
    'OrderModelSerializer',
    'AuditOrderModelSerializer'
]

from rest_framework import serializers


class BaseModelSerializer(serializers.ModelSerializer):
    is_draft = serializers.ReadOnlyField()
    is_active = serializers.ReadOnlyField()
    create_time = serializers.ReadOnlyField()
    last_modify_time = serializers.ReadOnlyField()

class DataModelSerializer(BaseModelSerializer):
    pass

class OrderModelSerializer(BaseModelSerializer):
    state = serializers.ReadOnlyField()

class AuditOrderModelSerializer(OrderModelSerializer):
    audit_state = serializers.ReadOnlyField()
