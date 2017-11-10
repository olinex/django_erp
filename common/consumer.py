#!/usr/bin/env python3
# -*- coding:utf-8 -*-

__all__ = ['http_login_required']


def http_login_required(func):
    """
    A decorator that will automatic ask the scoket to login
    :param func: a method of generic comsumer
    :return: wrapper of func
    """

    def wrapper(self, *args, **kwargs):
        if self.message.user and self.message.user.is_authenticated():
            return func(self, *args, **kwargs)
        else:
            self.message.reply_channel.send(
                {'accept': False, 'text': 'authenticate error', 'close': True})

    return wrapper
