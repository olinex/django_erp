#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from rest_framework import serializers, exceptions


class ActiveSerializer(serializers.Serializer):
    is_active = serializers.BooleanField(required=True)


class ActiveModelSerializer(serializers.ModelSerializer):
    is_active = serializers.BooleanField(read_only=True)


def StatePrimaryKeyRelatedField(cls, state, **kwargs):
    return serializers.PrimaryKeyRelatedField(
        queryset=cls.get_state_queryset(state),
        **kwargs
    )
