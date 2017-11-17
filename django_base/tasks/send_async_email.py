#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
@author:    olinex
@time:      2017/7/19 下午5:35
"""

__all__ = [
    'send_async_email', 'send_email_failure_callback', 'send_email_success_callback'
]

from celery import shared_task
from django_erp.common import responses
from celery.signals import task_failure, task_success
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model


@shared_task(name='send_async_email')
def send_async_email(
        user_pk, title, message, from_email,
        to_emails, context,
        connection=None, template='email.html',
        fail_silently=False
):
    """send email by using celery with broken"""
    from django.template import loader
    from django.core.mail import send_mail
    html = loader.get_template(template).render(context)
    return (send_mail(
        title,
        from_email=from_email,
        connection=connection,
        recipient_list=to_emails,
        fail_silently=fail_silently,
        message=message,
        html_message=html
    ), user_pk, title)


@task_success.connect(sender=send_async_email)
def send_email_success_callback(sender, result, **kwargs):
    if sender.name == 'send_async_email':
        User = get_user_model()
        result, user_pk, title = result
        print(user_pk)
        user = User.objects.get(pk=user_pk)
        if result > 0:
            user.socket_user(
                response=responses.NoticeSocketResponse(
                    user=user,
                    detail=_('send email success'),
                    content=_("the email '{}' was sended successfully").format(title)
                )
            )
        else:
            user.socket_user(
                response=responses.NoticeSocketResponse(
                    user=user,
                    detail=_('send email failed'),
                    content=_("the email '{}' was sended but server was no react with it").format(title),
                    status='warning'
                )
            )


@task_failure.connect(sender=send_async_email)
def send_email_failure_callback(sender, *args, **kwargs):
    if sender.name == 'send_async_email':
        User = get_user_model()
        user_pk, title = args[:2]
        user = User.objects.get(pk=user_pk)
        user.socket_user(
            response=responses.NoticeSocketResponse(
                user=user,
                detail=_('send email fail'),
                content=_("the email '{}' can not be send because the server side error").format(title),
                status='error'
            )
        )
