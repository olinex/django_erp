#!/usr/bin/env python3
# -*- coding:utf-8 -*-

__all__ = ['StateMachine', 'Statement']

from rest_framework import exceptions
from django.db import transaction
from django.db.models import Q


class StateMachine(object):
    """provide methods for model to manage statement"""
    objects = None

    class States:
        pass

    @classmethod
    def raise_state_exceptions(cls, *states):
        return exceptions.ValidationError(
            {state: cls.get_statement(state).error_message for state in states},
            code='not in state'
        )

    @classmethod
    def get_statement(cls, state):
        """get statement instances list"""
        return getattr(cls.States, state)

    def get_states_query(self, *states):
        """get statement query by list"""
        from functools import reduce
        return reduce(
            lambda a, b: a.query | b.query,
            [self.get_statement(state) for state in states]
        )

    @classmethod
    def get_states_queryset(cls, *states, queryset=None):
        """
        get queryset that filter by state's args and kwargs
        :param states: state symbol
        :param queryset: model queryset
        :return: queryset
        """
        query = cls.objects.all() if queryset is None else queryset
        return query.filter(cls.get_states_query(*states)).distinct()

    def check_states(self, *states, raise_exception=False):
        """
        check whether the instance's state is in states list
        :param states: list of state symbol string
        :param raise_exception: True/False
        :return: True/False
        """
        right_states = [state for state in states if self.get_statement(state).check(self)]
        if not right_states:
            if raise_exception:
                raise self.raise_state_exceptions(*states)
            return False
        return True and states

    def set_state(self, state):
        """
        set instance to statement
        :param state: state symbol
        :return: None
        """
        self.get_statement(state).set(self)

    def check_to_set_state(self, *check_states, set_state, raise_exception=False):
        """
        check whether the instance's state in check_states and set it to set_state
        :param check_states: list of state symbol string
        :param set_state: state symbol string
        :param raise_exception: True/False
        :return: True/False
        """
        statement = self.get_statement(set_state)
        with transaction.atomic():
            instance = self.__class__.objects.select_for_update().get(pk=self.pk)
            if instance.check_states(*check_states, raise_exception=raise_exception):
                statement.set(self)
                return True
            return False

    @classmethod
    def check_states_queryset(cls, *states, queryset, raise_exception=False):
        """
        check queryset wether in states
        :param states: list of state symbol string
        :param queryset: model queryset
        :param raise_exception: True/False
        :return: True/False
        """
        if queryset.exclude(cls.get_states_query(*states)).exists():
            if raise_exception:
                raise cls.raise_state_exceptions(*states)
            return False
        return True

    @classmethod
    def set_state_queryset(cls, state, queryset):
        """
        set queryset to state's params
        :param state: state symbol
        :param queryset: model queryset
        :return: None
        """
        queryset.update(**cls.get_statement(state).kwargs)

    @classmethod
    def check_to_set_state_queryset(cls, check_states, end_state, queryset, raise_exception=False):
        """
        check queryset is check_state then set them to end_state
        :param check_states: state symbol
        :param end_state: state symbol
        :param queryset: model queryset
        :param raise_exception: True/False
        :return: True/False
        """
        with transaction.atomic():
            if cls.check_states_queryset(
                    *check_states,
                    queryset=queryset.select_for_update(),
                    raise_exception=raise_exception
            ):
                cls.set_state_queryset(end_state, queryset=queryset)
                return True
            return False

    @classmethod
    def get_to_set_state_queryset(cls, check_state, end_state, queryset):
        """
        get queryset by check_state and set them to end_state
        :param check_state: state symbol
        :param end_state: state symbol
        :param queryset: model queryset
        :return: None
        """
        with transaction.atomic():
            check_queryset = cls.get_states_queryset(
                check_state, queryset=queryset.select_for_update()
            )
            cls.set_state_queryset(end_state, queryset=check_queryset)


class Statement(object):
    """model's statement define in States inner class"""

    def __init__(self, inherits=None, error_message='state error', **kwargs):
        self.kwargs = kwargs
        self.error_message = error_message
        if inherits is None:
            return
        if not isinstance(inherits, (list, tuple, set)):
            inherits = [inherits]
        for state in (inherits or []):
            self.kwargs.update(state.kwargs)

    @property
    def query(self):
        """return the statement's filter query"""
        from functools import reduce
        query = tuple(Q(**{key: value}) for key, value in self.kwargs.items())
        return reduce(lambda q1, q2: q1 & q1, query)

    def check(self, instance):
        for field, value in self.kwargs.items():
            if getattr(instance, field) != value:
                break
        else:
            return True
        return False

    def set(self, instance):
        for key, value in self.kwargs:
            setattr(instance, key, value)
        instance.save(update_fields=self.kwargs.keys())
