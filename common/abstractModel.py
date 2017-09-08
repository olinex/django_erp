#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from django.db import transaction
from django.db.models import F, Value, Func, Q
from django.utils.translation import ugettext_lazy as _

from apps.djangoperm import models
from . import state
from .state import StateMachine,Statement


class BaseModel(models.Model, state.StateMachine):
    '''
    the base model contain the status fields of active and delete,contain all the state method
    '''

    is_active = models.BooleanField(
        _('status of active'),
        blank=False,
        default=True,
        help_text=_('the status of active,True means active,False means not active')
    )

    is_delete = models.BooleanField(
        _('status of delete'),
        blank=False,
        default=False,
        help_text=_('the status of delete,True means have been deleted,False means have not be deleted')
    )

    create_time = models.DateTimeField(
        _('create time'),
        null=False,
        blank=False,
        auto_now_add=True,
        help_text=_('will auto write when create this node')
    )

    last_modify_time = models.DateTimeField(
        _('last modify time'),
        null=False,
        blank=False,
        auto_now=True,
        help_text=_('will auto write time when create or modify this node')
    )

    class Meta:
        abstract = True

    class States:
        delete = state.Statement(is_delete=True)
        no_delete = state.Statement(is_delete=False)
        active = state.Statement(inherits=no_delete, is_active=True)
        no_active = state.Statement(inherits=no_delete, is_active=False)


class CoordinateModel(models.Model):
    '''
    contain fields longitude and latitude
    '''

    lng = models.DecimalField(
        _('longitude'),
        null=True,
        blank=True,
        max_digits=9,
        decimal_places=6,
        default=None,
        help_text=_('max +180.000000,min -180.000000')
    )

    lat = models.DecimalField(
        _('latitude'),
        null=True,
        blank=True,
        max_digits=9,
        decimal_places=6,
        default=None,
        help_text=_('max +90.000000,min -90.000000')
    )

    class Meta:
        abstract = True

class TreeModel(models.Model,StateMachine):
    '''the abstract model for tree,contain three fields parent_node,index,level'''

    parent_node = models.ForeignKey(
        'self',
        null=True,
        default=None,
        verbose_name=_('parent node'),
        related_name='child_nodes',
        help_text=_('the parent node of the node')
    )

    index = models.CharField(
        _('tree index'),
        null=False,
        blank=True,
        default='-',
        max_length=190,
        help_text=_(
            '''
            tree index of the node,like "-a-b-c-",enumerate all of the parent node,
            if this node is the root node of tree,the index will be empty string
            '''
        )
    )

    class Meta:
        abstract = True

    class States:
        root = Statement(Q(parent_node=None) & Q(index=''))

    @property
    def level(self):
        if self.index != '-':
            return len(self.index.split('-')) - 2
        else:
            return 0

    @property
    def root_node(self):
        '''
        return the root parent node of this node in the same tree
        :return: common.TreeModel Instance
        '''
        if self.index != '':
            return self.__class__.objects.get(
                pk=int(self.index.split('-')[1])
            )
        return self

    @property
    def all_child_nodes(self):
        '''
        return all child node queryset of this node in the same tree
        :return: common.TreeModel Queryset
        '''
        return self.__class__.objects.filter(
            index__startswith='{}{}-'.format(self.index, self.id)
        )

    @property
    def all_parent_nodes(self):
        '''
        return all parent node queryset of this node in the same tree
        :return: common.TreeModel Queryset
        '''
        return self.__class__.objects.filter(
            pk__in=[int(node_pk) for node_pk in self.index.split('-')[1:-1]]
        )

    @property
    def sibling_nodes(self):
        '''
        return the node queryset which belongs to the same parent node,but exclude itself,
        if this node is a root node,will return all other root node
        :return: common.TreeModel Queryset
        '''
        return self.__class__.objects.filter(
            index=self.index
        ).exclude(pk=self.pk)

    @property
    @classmethod
    def root_nodes(cls):
        '''
        return the queryset of all root nodes
        :return: common.TreeModel Queryset
        '''
        return cls.objects.filter(
            parent_node=None,
            index='-'
        )

    def change_parent_node(self, parent):
        '''
        change this node's parent node,and child nodes's index
        :parent: common.TreeModel Instance
        :return: self
        '''
        with transaction.atomic():
            if parent == self.parent_node:
                return None
            if parent:
                node = self.__class__.objects.select_for_update().get(pk=parent.pk)
                new_index = '{}{}-'.format(node.index, str(node.pk))
            else:
                node=None
                new_index = '-'
            old_index = self.index
            self.all_child_nodes.select_for_update().update(
                index=Func(F('index'), Value(new_index), Value(old_index), function='replace')
            )
            self.index = new_index
            self.parent_node = node
            self.save()
            return self
