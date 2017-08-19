#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from collections import Iterable
from django.db import transaction
from django.db.models import Q


class StateMachine(object):
    '''provide methods for model to manage statement'''
    objects = None

    class States:
        pass

    def check_states(self,*states):
        '''
        check whether the instance's state is in states list
        :param states: list of state symbol string
        :return: True/False
        '''

        return self.__class__.objects.select_for_update().filter(
            Q(pk=self.pk) &
            self.__get_states_query(*states)
        ).exists()

    def set_state(self, state):
        '''
        set instance to statement
        :param state: state symbol
        :return: True/False
        '''
        statement = self.get_statement(state)
        self.__class__.objects.filter(pk=self.pk).update(
            **statement.kwargs
        )
        self.refresh_from_db()

    def check_to_set_state(self, *check_states,set_state):
        '''
        check whether the instance's state in check_states and set it to set_state
        :param check_states: list of state symbol string
        :param set_state: state symbol string
        :return: True/False
        '''
        set_statement = self.get_statement(set_state)
        with transaction.atomic():
            instance = self.__class__.objects.select_for_update().filter(
                Q(pk=self.pk) &
                self.__get_states_query(*check_states)
            )
            if instance:
                instance.update(**set_statement.kwargs)
                self.refresh_from_db()
                return True
            return False

    def get_statement(self, state):
        '''get statement instance'''
        return getattr(self.States, state)

    def __get_states_query(self,*states):
        '''get statement instances by list'''
        from functools import reduce
        if len(states) > 1:
            return reduce(
                lambda a,b:a.query | b.query,
                [self.get_statement(state) for state in states]
            )
        statement = self.get_statement(states[0])
        return statement.query

    @classmethod
    def check_state_queryset(cls,state,queryset):
        '''
        check the queryset is that all in state
        :param state: state symbol
        :param queryset: model queryset
        :return: True/False
        '''
        statement=getattr(cls.States,state)
        return not queryset.exclude(statement.query).exists()

    @classmethod
    def get_state_instance(cls,state,queryset=None):
        query = cls.objects.all() if not queryset else queryset
        statement = getattr(cls.States, state)
        return query.get(statement.query)

    @classmethod
    def get_state_queryset(cls,state,queryset=None):
        '''
        get queryset that filter by state's args and kwargs
        :param state: state symbol
        :return: queryset
        '''
        query = cls.objects.all() if not queryset else queryset
        statement=getattr(cls.States,state)
        return query.filter(statement.query).distinct()

    @classmethod
    def set_state_queryset(cls,state,queryset):
        '''
        set queryset to state's params
        :param state: state symbol
        :param queryset: model queryset
        :return: None
        '''
        statement=getattr(cls.States,state)
        queryset.update(**statement.kwargs)

    @classmethod
    def check_to_set_state_queryset(cls,check_state,end_state,queryset):
        '''
        check queryset is check_state then set them to end_state
        :param check_state: state symbol
        :param end_state: state symbol
        :param queryset: model queryset
        :return: True/False
        '''
        with transaction.atomic():
            filter_queryset=queryset.select_for_update()
            if cls.check_state_queryset(check_state,filter_queryset):
                cls.set_state_queryset(end_state,filter_queryset)
                return True
            return False

    @classmethod
    def get_to_set_state_queryset(cls,check_state,end_state,queryset=None):
        '''
        get queryset by check_state and set them to end_state
        :param check_state: state symbol
        :param end_state: state symbol
        :return: None
        '''
        with transaction.atomic():
            check_queryset=cls.get_state_queryset(
                check_state,queryset=queryset
            ).select_for_update()
            cls.set_state_queryset(end_state,queryset=check_queryset)


class Statement(object):
    '''model's statement define in States inner class'''

    def __init__(self, *args, inherits=None,error_message='', **kwargs):
        self.kwargs = kwargs
        self.args = args
        self.error_message = error_message
        if inherits:
            try:
                for state in inherits:
                    self.kwargs.update(state.kwargs)
                    self.args += state.args
            except:
                self.kwargs.update(inherits.kwargs)
                self.args += inherits.args

    @property
    def query(self):
        '''return the statement's filter query'''
        from functools import reduce
        query = self.args
        query += tuple(Q(**{key: value}) for key, value in self.kwargs.items())
        return reduce(lambda Q1,Q2:Q1 & Q2,query)


class StateSet(object):
    '''状态集'''
