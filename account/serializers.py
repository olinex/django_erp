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

    def update(self, instance, validated_data):
        validated_data.pop('phone',None)
        models.Profile.objects.update(user=instance.user,**validated_data)
        return instance

class UserSerializer(serializers.ModelSerializer):
    username=serializers.ReadOnlyField
    email=serializers.ReadOnlyField
    profile=ProfileSerializer()
    class Meta:
        model=User
        fields=('id','username','first_name','last_name','email','profile')

    def update(self, instance, validated_data):
        '''
        更新user以及profile,并屏蔽username/email/phone的修改
        '''
        with transaction.atomic():
            validated_data.pop('username',None)
            validated_data.pop('email',None)
            profile_data=validated_data.pop('profile',{})
            User.objects.update(id=instance.id,**validated_data)
            ProfileSerializer().update(
                instance=instance.profile,
                validated_data=profile_data)
            return instance

class LoginSerializer(serializers.ModelSerializer):
    username=serializers.CharField
    password=serializers.CharField
    class Meta:
        model=User
        fields=('username','password')