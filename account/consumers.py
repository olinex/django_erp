#!/usr/bin/env python3
#-*- coding:utf-8 -*-

import json
from .forms import TalkForm
from common import Redis
from common.notice import Notice,Talk,Response
from common.consumer import http_login_required
from channels import Group, Channel
from channels.generic.websockets import WebsocketConsumer
from django.utils.translation import ugettext_lazy as _

online_group = 'online_users'

class Server(WebsocketConsumer):
    '''
    Basic login server
    '''
    http_user = True

    @http_login_required
    def connect(self,message,**kwargs):
        channel=message.reply_channel
        user=message.user
        redis=Redis()
        redis.hset(online_group,str(user.id),message.reply_channel.name)
        if user.profile.online_notice:
            notice=Notice(
                user=user,
                detail=_('已经上线'),
                content='',
                status='info')
            group=Group(online_group)
            group.send({'text':notice.to_json()})
            group.add(channel)
        response=Response(detail='成功连接')
        channel.send({'accept':True,'text':response.to_json()})

    @http_login_required
    def disconnect(self, message, **kwargs):
        channel=message.reply_channel
        user=message.user
        redis=Redis()
        group=Group(online_group)
        group.discard(channel)
        notice=Notice(
            user=user,
            detail=_('已经离线'),
            content='',
            status='info')
        if user.profile.online_notice:
            group.send({'text':notice.to_json()})
        redis.hdel(online_group,str(user.id))
        response=Response(detail='成功断开连接')
        channel.send({'accept':True,'close':True,'text':response.to_json()})


    @http_login_required
    def receive(self, text=None, bytes=None, **kwargs):
        data=json.loads(text)
        request_type=data.get('type',None)
        listener=data.get('to_user',None)
        message=self.message
        if not listener or not request_type:
            message.reply_channel.send({
                'accept':False,
                'text':Response(
                    detail='请求必须包含type和to_user',
                    status='error'
                ).to_json()
            })
            return None
        if listener == message.user.id:
            message.reply_channel.send({
                'accept':False,
                'text':Response(
                    detail='请求to_user不能为自身',
                    status='error'
                ).to_json()
            })
            return None
        redis=Redis()
        channel_name=redis.hget(online_group,str(listener))
        if not channel_name:
            message.reply_channel.send({
                'accept':False,
                'text':Response(
                    detail='对方尚未上线',
                    status='warning'
                ).to_json()
            })
            return None
        form=TalkForm(data={
            'listener':listener,
            'talker':message.user.id,
            'content':data['content']
        })
        if not form.is_valid():
            message.reply_channel.send({
                'accept':False,
                'text':Response(
                    detail='无效的输入内容',
                    status='warning'
                ).to_json()
            })
            return None
        talk=Talk(
            user=message.user,
            detail='新私聊',
            content=form.cleaned_data['content'],
            status='success'
        )
        Channel(channel_name).send({
            'accept':True,
            'text':talk.to_json()})
