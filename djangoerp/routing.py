#!/usr/bin/env python3
#-*- coding:utf-8 -*-

from channels.routing import route_class
from account.consumers import  Server
channel_routing = [
    route_class(Server,path=r'^/$'),
]