#!/usr/bin/env python3
# -*- coding:utf-8 -*-

__all__ = ['Base']

import json
from ..serializers import TalkSerializer
from django_erp.common import Redis
from django_erp.common import responses
from django_erp.common.consumer import http_login_required
from channels import Group, Channel
from channels.generic.websockets import WebsocketConsumer
from django.utils.translation import ugettext as _

online_group = 'online_users'


class Base(WebsocketConsumer):
    """
    Basic login server
    """
    http_user = True

    @http_login_required
    def connect(self, message, **kwargs):
        channel = message.reply_channel
        user = message.user
        redis = Redis()
        redis.hset(online_group, str(user.id), message.reply_channel.name)
        if user.profile.online_notice:
            notice = responses.NoticeSocketResponse(
                user=user,
                detail=_('online'),
                content='',
                status='info')
            group = Group(online_group)
            group.send({'text': notice.to_json()})
            group.add(channel)
        response = responses.SocketResponse(detail=_('connected successfully'))
        channel.send({'accept': True, 'text': response.to_json()})

    @http_login_required
    def disconnect(self, message, **kwargs):
        channel = message.reply_channel
        user = message.user
        redis = Redis()
        group = Group(online_group)
        group.discard(channel)
        notice = responses.NoticeSocketResponse(
            user=user,
            detail=_('leave'),
            content='',
            status='info')
        if user.profile.online_notice:
            group.send({'text': notice.to_json()})
        redis.hdel(online_group, str(user.id))
        response = responses.SocketResponse(detail=_('disconnected successfully'))
        channel.send({'accept': True, 'close': True, 'text': response.to_json()})

    @http_login_required
    def receive(self, text=None, bytes=None, **kwargs):
        data = json.loads(text)
        request_type = data.get('type', None)
        listener = data.get('to_user', None)
        message = self.message
        if not listener or not request_type:
            message.reply_channel.send({
                'accept': False,
                'text': responses.SocketResponse(
                    detail=_('request must have the params "type" and "to_user"'),
                    status=_('error')
                ).to_json()
            })
            return None
        if listener == message.user.id:
            message.reply_channel.send({
                'accept': False,
                'text': responses.SocketResponse(
                    detail=_('request can not be himself'),
                    status=_('error')
                ).to_json()
            })
            return None
        redis = Redis()
        channel_name = redis.hget(online_group, str(listener))
        if not channel_name:
            message.reply_channel.send({
                'accept': False,
                'text': responses.SocketResponse(
                    detail=_("your friend did't login yet"),
                    status=_('warning')
                ).to_json()
            })
            return None
        serializer = TalkSerializer(data={
            'listener': listener,
            'talker': message.user.id,
            'content': data['content']
        })
        if not serializer.is_valid():
            message.reply_channel.send({
                'accept': False,
                'text': responses.SocketResponse(
                    detail=_('not valid content'),
                    status=_('warning')
                ).to_json()
            })
            return None
        talk = responses.TalkSocketResponse(
            user=message.user,
            detail=_('new talk'),
            content=serializer.validated_data['content'],
            status=_('success')
        )
        Channel(channel_name).send({
            'accept': True,
            'text': talk.to_json()})
