#!/usr/bin/env python3
# -*- coding:utf-8 -*-

'''
@author:    olinex
@time:      2017/7/19 下午5:35
'''

from celery import shared_task
from django.conf import settings

@shared_task
def send_email(
        title,message,to_emails,username,
        from_email=settings.DEFAULT_FROM_EMAIL,
        auth_user=settings.EMAIL_HOST_USER,
        auth_password=settings.EMAIL_HOST_PASSWORD,
        fail_silently=False,context=None
):
    '''send email by using celery with broken'''
    from django.core.mail import send_mail
    from django.template import loader
    default = {'title':title,'message':message,'username':username}
    data = context or default
    data.update(**default)
    html = loader.get_template('email.html').render(data)
    send_mail(
        title,
        message=message,
        from_email=from_email,
        auth_user=auth_user,
        auth_password=auth_password,
        recipient_list=to_emails,
        fail_silently=fail_silently,
        html_message=html
    )
    return True