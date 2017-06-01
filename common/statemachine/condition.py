#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from django.apps import apps
from django.db import transaction


class Condition(object):
    '''conbine model's statement that to be a single condition'''
    begin_states = ()
    end_states = ()

    def __init__(self,begin_instances,end_instances):
        if len(begin_instances) == len(self.begin_states):
            if len(end_instances) == len(self.end_states):
                self.begin = zip(begin_instances,self.begin_states)
                self.end = zip(end_instances,self.end_states)
            else:
                raise AttributeError('the length of end_states must equal to end_instances')
        else:
            raise AttributeError('the length of begin_states must equal to begin_instances')

    @staticmethod
    def _get_model(state_str):
        app_label, model_name, state = state_str.split('.')
        return (apps.get_model(app_label, model_name), state)

    def check_begin_states(self, from_db=False):
        for state_str,instance in self.begin:
            model, state = self._get_model(state_str)
            if not instance.check_state(state, from_db=from_db):
                return False
        return True

    def set_end_states(self):
        with transaction.atomic():
            for state_str,instance in self.end:
                model, state = self._get_model(state_str)
                if not instance.set_state(state):
                    raise ValueError('{} can not be set to state of {}'.format(instance,state))
