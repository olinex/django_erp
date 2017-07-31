#!/usr/bin/env python3
#-*- coding:utf-8 -*-

from django import forms
from django.contrib.auth import get_user_model

User=get_user_model()

class TalkForm(forms.Form):
    talker=forms.ModelChoiceField(queryset=User.objects.filter(is_active=True))
    listener=forms.ModelChoiceField(queryset=User.objects.filter(is_active=True))
    content=forms.CharField(max_length=90,min_length=5)