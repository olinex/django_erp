#!/usr/bin/env python3
#-*- coding:utf-8 -*-

class JsonSerializer(object):
    STATUS_TYPES=('success','info','warning','error')
    def check_status(self):
        if status not in self.STATUS_TYPES:
            raise AttributeError(
                'status must be a string of {}'.format(
                    '/'.join(self.STATUS_TYPES)))


    def to_json(self):
        '''
        返回对象的Json数据
        :return: json data string
        '''
        import json
        data = self.get_data()
        return json.dumps(data)

class Response(JsonSerializer):
    '''长连接的响应类,只包含响应状态和明细'''
    def __init__(self,detail,status='success'):
        self.detail=detail
        self.status=status

    def get_data(self):
        self.check_status()
        return {
            'type':'response',
            'detail':self.detail,
            'status':self.status
        }


class Notice(JsonSerializer):
    '''拥有特定构造函数的通知类'''

    def __init__(self,user,detail,content,status='success'):
        self.check_status()
        self.user=user
        self.detail=detail
        self.content=content
        self.status=status

    def update(self,**kwargs):
        self.check_status()
        self.user=kwargs.get('user',self.user)
        self.detail=kwargs.get('detail',self.detail)
        self.content=kwargs.get('content',self.content)
        self.status=kwargs.get('status',self.status)

    def get_data(self):
        self.check_status()
        return {
            'user_id':self.user.id,
            'username':self.user.get_full_name() or self.user.get_username(),
            'type':'notice',
            'detail':self.detail,
            'content':self.content,
            'status':self.status
        }

class Talk(Notice):
    '''拥有特定构造函数的谈话类'''
    def get_data(self):
        data=super(Talk,self).get_data()
        data['type']='talk'
        return data
