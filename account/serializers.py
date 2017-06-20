#!/usr/bin/env python3
#-*- coding:utf-8 -*-

from . import models
from django.db import transaction
from rest_framework import serializers,exceptions
from common.rest.serializers import ActiveModelSerializer
from django.contrib.auth import get_user_model

User=get_user_model()


class ProvinceSerializer(ActiveModelSerializer):
    class Meta:
        model=models.Province
        fields=('id','country','name','is_active')

class CitySerializer(ActiveModelSerializer):
    class Meta:
        model=models.City
        fields=('id','province','name','is_active')

class RegionSerializer(ActiveModelSerializer):
    class Meta:
        model=models.Region
        fields=('id','city','name','is_active')

class AddressSerializer(ActiveModelSerializer):
    province_detail=ProvinceSerializer(
        source='region.city.province',
        read_only=True
    )
    city_detail=CitySerializer(
        source='region.city',
        read_only=True
    )
    region_detail=RegionSerializer(
        source='region',
        read_only=True
    )
    class Meta:
        model=models.Address
        fields=(
            'id','region','name','is_active',
            'province_detail','city_detail','region_detail'
        )

class ProfileSerializer(serializers.ModelSerializer):
    user=serializers.ReadOnlyField()
    phone=serializers.ReadOnlyField(read_only=True)
    usual_send_addresses_detail=AddressSerializer(
        source='usual_send_addresses',
        read_only=True,
        many=True
    )

    class Meta:
        model=models.Profile
        fields=(
            'user','sex','phone','language','mail_notice','online_notice',
            'address','default_send_address','usual_send_addresses',
            'salable','purchasable','is_partner',
            'usual_send_addresses_detail'
        )

    def update(self, instance, validated_data):
        validated_data.pop('user',None)
        return super(ProfileSerializer,self).update(instance, validated_data)

class PasswordSerializer(serializers.ModelSerializer):
    password1=serializers.CharField(required=True)
    password2=serializers.CharField(required=True)
    class Meta:
        model=User
        fields=('password1','password2')

    def validate(self,data):
        from django.contrib.auth import password_validation
        password1=data.get('password1')
        password2=data.get('password2')
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
    email = serializers.CharField(read_only=True)
    profile=ProfileSerializer(partial=True)
    permissions=serializers.SerializerMethodField(read_only=True)
    class Meta:
        model=User
        fields=(
            'id','username','first_name','last_name',
            'is_active','email','profile',
            'permissions'
        )

    def create(self, validated_data):
        profile_data=validated_data.pop('profile',{})
        user=super(UserSerializer,self).create(validated_data)
        profile_data['user']=user.id
        ProfileSerializer().create(profile_data)
        return user

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

class CompanySerializer(ActiveModelSerializer):
    usual_send_addresses_detail=AddressSerializer(
        source='usual_send_addresses',
        read_only=True,
        many=True
    )
    belong_users_detail=UserSerializer(
        source='belong_customers',
        read_only=True,
        many=True
    )
    class Meta:
        model=models.Company
        fields=(
            'id','name','tel','is_active','address',
            'default_send_address','usual_send_addresses',
            'usual_send_addresses_detail',
            'salable','purchasable',
            'belong_users',
            'belong_users_detail'
        )
