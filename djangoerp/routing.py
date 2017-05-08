#!/usr/bin/env python3
#-*- coding:utf-8 -*-

from channels.routing import route_class
from account import  consumers
channel_routing = [
    route_class(consumers.LoginServer,path=r'^/$'),
    route_class(consumers.PrivateTalkServer,path=r'^/private/(?P<user>\d+)_id/$'),
]