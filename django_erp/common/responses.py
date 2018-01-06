#!/usr/bin/env python3
# -*- coding:utf-8 -*-

__all__ = [
    'JsonSerializer',
    'SocketResponse',
    'NoticeSocketResponse',
    'TalkSocketResponse'
]

from django.utils import timezone
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.translation import ugettext_lazy as _


class JsonSerializer(object):
    status = ''
    STATUS_TYPES = ('success', 'info', 'warning', 'error')

    def get_data(self):
        return {}

    def check_status(self):
        if self.status not in self.STATUS_TYPES:
            raise AttributeError(
                _('status must be a string of {}').format(
                    '/'.join(self.STATUS_TYPES))
            )

    def to_json(self):
        """
        convert data to json string
        :return: json data string
        """
        import json
        self.check_status()
        data = self.get_data()
        return json.dumps(data, cls=DjangoJSONEncoder,sort_keys=True)


class SocketResponse(JsonSerializer):
    """
    the long time connect response
    """

    def __init__(self, detail, status='success'):
        self.detail = detail
        self.status = status

    def get_data(self):
        return {
            'type': 'response',
            'detail': self.detail,
            'status': self.status
        }


class NoticeSocketResponse(JsonSerializer):
    """
    the response for return notice
    """

    def __init__(self, user, detail, content, status='success'):
        self.user = user
        self.detail = detail
        self.content = content
        self.status = status

    def get_data(self):
        return {
            'user_id': self.user.id,
            'username': self.user.get_full_name() or 'user_{}'.format(self.user.id),
            'avatar': self.user.avatar.url,
            'type': 'notice',
            'detail': self.detail,
            'content': self.content,
            'status': self.status,
            'create_time': timezone.now()
        }


class TalkSocketResponse(JsonSerializer):
    """
    the response for return talk
    """
    def __init__(self, from_user, to_user_id, detail, content, status='success'):
        self.from_user = from_user
        self.to_user_id = to_user_id
        self.detail = detail
        self.content = content
        self.status = status

    def get_data(self):
        return {
            'from_user_id': self.from_user.id,
            'to_user_id': self.to_user_id,
            'from_username': self.from_user.get_full_name() or 'user_{}'.format(self.from_user.id),
            'avatar': self.from_user.avatar.url,
            'type': 'talk',
            'detail': self.detail,
            'content': self.content,
            'status': self.status,
            'create_time': timezone.now()
        }
