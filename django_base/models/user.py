#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
@author:    olinex
@time:      2017/11/9 上午11:39
"""

__all__ = ['User']

from django_perm.db import models
from django.conf import settings
from django_erp.common import Redis
from django.utils.translation import ugettext_lazy as _
from channels import Channel
from django.contrib.auth.models import AbstractUser
from ..tasks import send_async_email


class User(AbstractUser):
    """customer for the project"""
    SEX_CHOICES = (
        ('unknown', _('unknown')),
        ('male', _('male')),
        ('female', _('female')),
    )

    avatar = models.ImageField(
        upload_to='image/base/user/avatar',
        default='image/base/user/avatar/default.png',
        null=False,
        blank=False,
        verbose_name=_('avatar'),
        help_text=_("the relate path of the user avatar")
    )

    sex = models.CharField(
        _('sex'),
        null=False,
        default='unknown',
        max_length=10,
        choices=SEX_CHOICES,
        help_text=_("the sex of the user")
    )

    phone = models.CharField(
        _('phone'),
        max_length=11,
        null=True,
        blank=False,
        unique=True,
        default=None,
        help_text=_("the user's phone number")
    )

    language = models.CharField(
        _('language'),
        null=True,
        blank=False,
        default='zh-han',
        max_length=20,
        choices=settings.LANGUAGES,
        help_text=_("user's mother language")
    )

    address = models.ForeignKey(
        'Address',
        null=True,
        blank=False,
        help_text=_("user's address")
    )

    mail_notice = models.BooleanField(
        _('nail notice'),
        default=True,
        help_text=_("True means that user will receive mail on the web")
    )

    online_notice = models.BooleanField(
        _('online notice'),
        default=False,
        help_text=_("True means that user will tell others user's online status")
    )

    def __str__(self):
        return '{}-{}'.format(
            self.id,
            self.get_full_name() or self.get_username()
        )

    @staticmethod
    def _message_cache_name(pk):
        return 'message_user_{}'.format(pk)

    @property
    def message_cache_name(self):
        return self._message_cache_name(self.pk)

    @property
    def channel(self):
        redis = Redis()
        channel_name = redis.hget(settings.SOCKET_ONLINE_GROUP_NAME, str(self.pk))
        if channel_name:
            channel_name = channel_name.decode('utf8')
            return Channel(channel_name)
        return None

    def register_online_group(self, message):
        """reigister user to online group when socket message was received"""
        redis = Redis()
        redis.hset(
            settings.SOCKET_ONLINE_GROUP_NAME,
            str(self.pk),
            message.reply_channel.name
        )

    @classmethod
    def get_oline_users(cls):
        """get the """
        redis = Redis()
        return cls.objects.filter(
            id__in=redis.hgetall(settings.SOCKET_ONLINE_GROUP_NAME).keys()
        )

    def disregister_online_group(self):
        """disregister user from online group,notice that socket was not closed on that time"""
        redis = Redis()
        redis.hdel(
            settings.SOCKET_ONLINE_GROUP_NAME,
            str(self.pk)
        )

    def socket_user(self, response, close=False, accept=True):
        channel = self.channel
        if channel:
            channel.send({
                'accept': accept,
                'close': close,
                'text': response.to_json()})
            return True
        return False

    @property
    def new_messages(self):
        """
        get new messages according to redis
        :return: message queryset
        """
        from .message import Message
        redis = Redis()
        return Message.objects.filter(
            pk__in=redis.smembers(self.message_cache_name)
        )

    def remove_message(self, message):
        """
        remove the message
        :return: None
        """
        redis = Redis()
        redis.srem(self.message_cache_name, message.pk)

    def clear_messages(self):
        """
        remove all of the messages
        :return: None
        """
        redis = Redis()
        redis.delete(self.message_cache_name)

    def async_email_user(self, subject, message, to_emails, template='email.html', fail_silently=False, **kwargs):
        """send email by using the email account and celerr task"""
        if self.email and self.emailaccount.objects.exists():
            email = self.email
            connection = self.emailaccount.connection
        else:
            email = settings.DEFAULT_FROM_EMAIL
            connection = None
        send_async_email.delay(
            user=self.pk,
            title=subject,
            message=message,
            from_email=email,
            to_emails=to_emails,
            context=kwargs,
            template=template,
            connection=connection,
            fail_silently=fail_silently
        )

