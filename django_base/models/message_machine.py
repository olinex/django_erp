#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
@author:    olinex
@time:      2017/11/15 下午1:31
"""

__all__ = ['MessageMachine']

from django_perm.db import models
from django_erp.common import Redis
from django.db import transaction
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.fields import GenericRelation


class MessageMachine(models.Model):
    """
    the model contain the method to create the message
    """
    followers = models.JSONField(
        _('followers'),
        form='list',
        default=[],
        help_text=_("the users will receive notice when message wwas created")
    )

    def add_followers(self, *users):
        """
        add user to instance's follower to receive notice
        :param users: user object set
        :return: None
        """
        followers = set(self.followers) | set(user.pk for user in users)
        if len(followers) != len(self.followers):
            self.followers = list(followers)
            self.save(update_fields=['followers'])

    def remove_followers(self, *users):
        """
        remove user from instance's follower
        :param users: user object set
        :return: None
        """
        followers = set(self.followers) ^ set(user.pk for user in users)
        if len(followers) != len(self.followers):
            self.followers = list(followers)
            self.save(update_fields=['followers'])

    def clear_followers(self):
        """
        remove all of the followers
        :return: None
        """
        self.followers = []
        self.save(update_fields=['followers'])

    def create_message(self, title, text, creater):
        """
        create message of the instance
        :param title: string
        :param text: string
        :param creater: user object
        :return: message object
        """
        from ..models import Message
        from ..utils import get_argument
        with transaction.atomic():
            message = Message.objects.create(
                title=title,
                text=text,
                creater=creater,
                instance=self
            )
            redis = Redis()
            if get_argument('add_follower_after_create_message'):
                self.add_followers(creater)
            for user_id in filter(lambda follower: follower != creater.id,self.followers):
                redis.sadd(
                    creater._message_cache_name(user_id),
                    message.pk
                )
            return message

    messages = GenericRelation('django_base.Message')

    class Meta:
        abstract = True
