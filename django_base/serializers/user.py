#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
@author:    olinex
@time:      2017/11/9 上午11:56
"""

__all__ = [
    'PasswordSerializer',
    'ResetPasswordSerializer',
    'UserSerializer',
    'LoginSerializer'
]

from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from .profile import ProfileSerializer

User = get_user_model()


class PasswordSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(required=True)
    password2 = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('password1', 'password2')

    def validate(self, data):
        from django.contrib.auth import password_validation
        password1 = data.get('password1')
        password2 = data.get('password2')
        if password1 and password2 and password1 != password2:
            raise serializers.ValidationError(_('password and password confirm is not same'))
        password_validation.validate_password(password2)
        return data

    def save(self):
        self.instance.set_password(
            self.validated_data['password2']
        )
        self.instance.save()


class ResetPasswordSerializer(serializers.ModelSerializer):
    old_password = serializers.CharField(required=True)
    new_password = PasswordSerializer(required=True)

    class Meta:
        model = User
        fields = ('old_password', 'new_password')

    def validate_old_password(self, value):
        if not self.instance.check_password(value):
            raise serializers.ValidationError(_('origin password not valid'))
        return value

    def save(self):
        serializer = PasswordSerializer(
            instance=self.instance,
            data=self.validated_data['new_password']
        )
        if serializer.is_valid(raise_exception=True):
            serializer.save()


class UserSerializer(serializers.ModelSerializer):
    email = serializers.CharField(read_only=True)
    profile_detail = ProfileSerializer(source='profile', read_only=True)
    permissions = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'id', 'username', 'first_name', 'last_name',
            'is_active', 'email', 'profile_detail', 'permissions'
        )

    def create(self, validated_data):
        password_data = validated_data.pop('new_password', {})
        user = super(UserSerializer, self).create(validated_data)
        PasswordSerializer(instance=user, data=password_data).save()
        return user

    def get_permissions(self, obj):
        """
        获取用户的所有权限
        """
        if obj.is_superuser:
            return {'__all__'}
        return obj.get_all_permissions()


class LoginSerializer(serializers.ModelSerializer):
    username = serializers.CharField
    password = serializers.CharField

    class Meta:
        model = User
        fields = ('username', 'password')


class CaptchaSerializer(serializers.Serializer):
    code = serializers.CharField

    def validate_code(self, val):
        pass
