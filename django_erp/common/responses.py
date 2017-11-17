#!/usr/bin/env python3
# -*- coding:utf-8 -*-

__all__ = [
    'JsonSerializer',
    'SocketResponse',
    'NoticeSocketResponse',
    'TalkSocketResponse'
]

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
        return json.dumps(data)


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

    def update(self, **kwargs):
        self.user = kwargs.get('user', self.user)
        self.detail = kwargs.get('detail', self.detail)
        self.content = kwargs.get('content', self.content)
        self.status = kwargs.get('status', self.status)

    def get_data(self):
        return {
            'user_id': self.user.id,
            'username': self.user.get_full_name() or self.user.get_username(),
            'type': 'notice',
            'detail': self.detail,
            'content': self.content,
            'status': self.status
        }


class TalkSocketResponse(NoticeSocketResponse):
    """
    the response for return talk
    """

    def get_data(self):
        data = super(TalkSocketResponse, self).get_data()
        data['type'] = 'talk'
        return data
