#!/usr/bin/env python3
# -*- coding:utf-8 -*-

__all__ = [
    'NoneSerializer',
    'IdListSerializer',
    'GroupSerializer',
    'PermissionsSerializer',
    'ContentTypeSerializer',
    'BaseModelSerializer',
    'DataModelSerializer',
    'OrderModelSerializer',
    'AuditOrderModelSerializer'
]

from rest_framework import serializers
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType


class NoneSerializer(serializers.Serializer):
    pass


class ContentTypeSerializer(serializers.ModelSerializer):
    app_label = serializers.ReadOnlyField()
    model = serializers.ReadOnlyField()

    class Meta:
        model = ContentType
        fields = '__all__'


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'


class PermissionsSerializer(serializers.ModelSerializer):
    content_type = ContentTypeSerializer(read_only=True)
    class Meta:
        model = Permission
        fields = '__all__'


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
    sequence = serializers.IntegerField(min_value=0, max_value=32767)


class DataModelSerializer(BaseModelSerializer, SequenceSerializer):
    pass


class OrderModelSerializer(BaseModelSerializer):
    state = serializers.ReadOnlyField()


class AuditOrderModelSerializer(OrderModelSerializer):
    audit_state = serializers.ReadOnlyField()
