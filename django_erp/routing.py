#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from channels.routing import route_class

from django_account.consumers import Base

channel_routing = [
    route_class(Base,path=r'^/$'),
]