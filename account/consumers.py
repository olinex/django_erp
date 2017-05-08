#!/usr/bin/env python3
#-*- coding:utf-8 -*-

import json
from .forms import TalkForm
from common import Redis
from common.consumer import http_login_required
from channels import Group, Channel
from channels.generic.websockets import WebsocketConsumer

online_group = 'online_users'

class LoginServer(WebsocketConsumer):
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
            group=Group(online_group)
            group.send({'text':json.dumps({
                'type':'loginNotice',
                'id':user.id,
                'username':user.get_full_name() or user.get_username()
            })})
            group.add(channel)
        channel.send({'accept':True,'text':'success'})

    @http_login_required
    def disconnect(self, message, **kwargs):
        print('logout connect')
        channel=message.reply_channel
        user=message.user
        redis=Redis()
        group=Group(online_group)
        group.discard(channel)
        if user.profile.online_notice:
            group.send({'text':json.dumps({
                'type':'logoutNotice',
                'id':user.id,
                'username':user.get_full_name() or user.get_username()
            })})
        redis.hdel(online_group,str(user.id))
        channel.send({'accept':True,'close':True,'text':'success'})

class PrivateTalkServer(WebsocketConsumer):
    '''
    ASGI WebSocket received
    '''
    http_user = True

    @http_login_required
    def receive(self,text=None,bytes=None,**kwargs):
        listener=kwargs['user']
        if listener == self.message.user.id:
            redis=Redis()
            channel_name=redis.hget(online_group,str(listener))
            if channel_name:
                form=TalkForm(data={
                    'listener':listener,
                    'talker':self.message.user.id,
                    'content':text
                })
                if form.is_valid():
                    print(self.message.reply_channel.name,channel_name)
                    Channel(channel_name).send({
                        'accept':True,
                        'text':form.cleaned_data['content']})
                else:
                    self.message.reply_channel.send({'accept':False,'text':'不合法的输入'})
            else:
                self.message.reply_channel.send({'accept':False,'text':'对方尚未上线'})
        else:
            self.message.reply_channel.send({'accept':False,'text':'不可对自身发起私聊'})
