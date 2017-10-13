#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from django_base.models import Address
from django_base.serializers import AddressSerializer
from common.rest.serializers import ActiveModelSerializer, StatePrimaryKeyRelatedField
from . import models

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


class ProfileSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    phone = serializers.ReadOnlyField()
    usual_send_addresses_detail = AddressSerializer(
        source='usual_send_addresses',
        read_only=True,
        many=True
    )
    mail_notice = serializers.ReadOnlyField()
    online_notice = serializers.ReadOnlyField()
    address = StatePrimaryKeyRelatedField(Address, 'active')
    default_send_address = StatePrimaryKeyRelatedField(Address, 'active', many=True)
    usual_send_addresses = StatePrimaryKeyRelatedField(Address, 'active', many=True)

    class Meta:
        model = models.Profile
        fields = (
            'user', 'sex', 'phone', 'language', 'mail_notice', 'online_notice',
            'address', 'default_send_address', 'usual_send_addresses',
            'usual_send_addresses_detail'
        )


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
        '''
        获取用户的所有权限
        '''
        if obj.is_superuser:
            return {'__all__'}
        return obj.get_all_permissions()


class MailNoticeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Profile
        fields = ('mail_notice',)


class OnlineNoticeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Profile
        fields = ('online_notice',)


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
