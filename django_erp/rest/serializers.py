#!/usr/bin/env python3
# -*- coding:utf-8 -*-

__all__ = [
    'NoneSerializer',
    'IdListSerializer',
    'BaseModelSerializer',
    'DataModelSerializer',
    'OrderModelSerializer',
    'AuditOrderModelSerializer'
]

from rest_framework import serializers

class NoneSerializer(serializers.Serializer):
    pass

class IdListSerializer(serializers.Serializer):
    ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        required=True,
        min_length=1,
        max_length=100
    )

class HistoryModelSerializer(serializers.ModelSerializer):
    create_time = serializers.ReadOnlyField()
    last_modify_time = serializers.ReadOnlyField()


class BaseModelSerializer(HistoryModelSerializer):
    is_draft = serializers.ReadOnlyField()
    is_active = serializers.ReadOnlyField()

class SequenceSerializer(serializers.ModelSerializer):
    sequence = serializers.IntegerField(min_value=0,max_value=32767)

class DataModelSerializer(BaseModelSerializer,SequenceSerializer):
    pass

class OrderModelSerializer(BaseModelSerializer):
    state = serializers.ReadOnlyField()

class AuditOrderModelSerializer(OrderModelSerializer):
    audit_state = serializers.ReadOnlyField()
