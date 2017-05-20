#!/usr/bin/env python3
#-*- coding:utf-8 -*-

from . import models
from django.db import transaction
from django.contrib.auth.models import User
from rest_framework import serializers,exceptions

class ProfileSerializer(serializers.ModelSerializer):
    phone=serializers.ReadOnlyField(required=False)
    class Meta:
        model=models.Profile
        fields=('sex','phone','online_notice','language','mail_notice')

    def create(self, validated_data):
        if not validated_data.get('user_id',None):
            raise serializers.ValidationError("profile must have user")
        return models.Profile.objects.create(**validated_data)

    def update(self, instance, validated_data):
        validated_data.pop('phone',None)
        models.Profile.objects.update(user=instance.user,**validated_data)
        return instance

class PasswordSerializer(serializers.ModelSerializer):
    password1=serializers.CharField(required=True)
    password2=serializers.CharField(required=True)
    class Meta:
        model=User
        fields=('password1','password2')

    def validate(self,data):
        from django.contrib.auth import password_validation
        password1=data['password1']
        password2=data['password2']
        if password1 and password2 and password1 != password2:
            raise serializers.ValidationError('密码以及确认密码不一致')
        password_validation.validate_password(password2)
        return data

    def save(self):
        self.instance.set_password(
            self.validated_data['password2']
        )
        self.instance.save()


class ResetPasswordSerializer(serializers.ModelSerializer):
    old_password=serializers.CharField(required=True)
    new_password=PasswordSerializer(required=True)
    class Meta:
        model=User
        fields=('old_password','new_password')

    def validate_old_password(self,value):
        if not self.instance.check_password(value):
            raise serializers.ValidationError('请输入正确的原始密码')
        return value

    def save(self):
        serializer=PasswordSerializer(
            instance=self.instance,
            data=self.validated_data['new_password']
        )
        if serializer.is_valid(raise_exception=True):
            serializer.save()


class UserSerializer(serializers.ModelSerializer):
    username=serializers.CharField(required=False)
    email=serializers.ReadOnlyField
    profile=ProfileSerializer()
    permissions=serializers.SerializerMethodField()
    new_password=PasswordSerializer(required=False)
    class Meta:
        model=User
        fields=(
            'id','username','first_name','last_name',
            'is_active','email','profile',
            'permissions','new_password')

    def create(self, validated_data):
        with transaction.atomic():
            profile_data=validated_data.pop('profile')
            user=User()
            user.username=validated_data['username']
            user.first_name=validated_data['first_name']
            user.last_name=validated_data['last_name']
            user.is_active=validated_data['is_active']
            password_data=validated_data.pop('new_password')
            password_serializer=PasswordSerializer(
                instance=user,
                data=password_data
            )
            if password_serializer.is_valid(raise_exception=True):
                password_serializer.save()
            user.save()
            profile_data['user_id']=user.id
            serializer=ProfileSerializer(data=profile_data)
            if serializer.is_valid(raise_exception=True):
                serializer.create(profile_data)
                return user

    def update(self, instance, validated_data):
        '''
        更新user以及profile,并屏蔽username/email/phone的修改
        '''
        with transaction.atomic():
            validated_data.pop('username')
            validated_data.pop('email')
            validated_data.pop('new_password')
            validated_data.pop('is_active')
            profile_data=validated_data.pop('profile',{})
            User.objects.update(id=instance.id,**validated_data)
            ProfileSerializer(instance.profile,data=profile_data).save()
            return instance

    def get_permissions(self,obj):
        '''
        获取用户的所有权限
        '''
        if obj.is_superuser:
            return { '__all__' }
        return obj.get_all_permissions()

class LoginSerializer(serializers.ModelSerializer):
    username=serializers.CharField
    password=serializers.CharField
    class Meta:
        model=User
        fields=('username','password')

class CaptchaSerializer(serializers.Serializer):
    code=serializers.CharField

    def validate_code(self,val):
        from django.contrib.auth import tokens
