#!/usr/bin/env python3
# -*- coding:utf-8 -*-

__all__ = [
    'CoordinateModel',
    'TreeModel',
    'HistoryModel',
    'BaseModel',
    'SequenceModel',
    'DataModel',
    'OrderModel',
    'AuditOrderModel'
]

from django.db import transaction
from django.db.models import F, Value, Func
from django.utils.translation import ugettext_lazy as _

from django_perm.db import models
from .state import StateMachine, Statement
from .fileds import OrderStateCharField, AuditStateCharField


class CoordinateModel(models.Model):
    """
    contain fields longitude and latitude
    """

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


class TreeModel(models.Model, StateMachine):
    """the abstract model for tree,contain three fields parent_node,index,level"""

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
            """
            tree index of the node,like '-a-b-c-',enumerate all of the parent node,
            if this node is the root node of tree,the index will be empty string
            """
        )
    )

    class Meta:
        abstract = True

    class States:
        root = Statement(parent_node=None, index='')

    @property
    def level(self):
        if self.index != '-':
            return len(self.index.split('-')) - 2
        else:
            return 0

    @property
    def root_node(self):
        """
        return the root parent node of this node in the same tree
        :return: common.TreeModel Instance
        """
        if self.index != '':
            return self.__class__.objects.get(
                pk=int(self.index.split('-')[1])
            )
        return self

    @property
    def all_child_nodes(self):
        """
        return all child node queryset of this node in the same tree
        :return: common.TreeModel Queryset
        """
        return self.__class__.objects.filter(
            index__startswith='{}{}-'.format(self.index, self.id)
        )

    @property
    def all_parent_nodes(self):
        """
        return all parent node queryset of this node in the same tree
        :return: common.TreeModel Queryset
        """
        return self.__class__.objects.filter(
            pk__in=[int(node_pk) for node_pk in self.index.split('-')[1:-1]]
        )

    @property
    def sibling_nodes(self):
        """
        return the node queryset which belongs to the same parent node,but exclude itself,
        if this node is a root node,will return all other root node
        :return: common.TreeModel Queryset
        """
        return self.__class__.objects.filter(
            index=self.index
        ).exclude(pk=self.pk)

    @property
    @classmethod
    def root_nodes(cls):
        """
        return the queryset of all root nodes
        :return: common.TreeModel Queryset
        """
        return cls.objects.filter(
            parent_node=None,
            index='-'
        )

    def change_parent_node(self, parent):
        """
        change this node's parent node,and child nodes's index
        :parent: common.TreeModel Instance
        :return: self
        """
        with transaction.atomic():
            if parent == self.parent_node:
                return None
            if parent:
                node = self.__class__.objects.select_for_update().get(pk=parent.pk)
                new_index = '{}{}-'.format(node.index, str(node.pk))
            else:
                node = None
                new_index = '-'
            old_index = self.index
            self.all_child_nodes.select_for_update().update(
                index=Func(F('index'), Value(new_index), Value(old_index), function='replace')
            )
            self.index = new_index
            self.parent_node = node
            self.save()
            return self


def action_factory(*from_state, to_state, name):
    def action(self, raise_exception=False):
        with transaction.atomic():
            self.check_states(*from_state, raise_exception=raise_exception)
            getattr(self, 'before_{}'.format(name))()
            self.set_state(to_state)
            getattr(self, 'after_{}'.format(name))()

    return action


class HistoryModel(models.Model, StateMachine):
    """
    the base model contain the create time and last modify time
    """
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
        ordering = ['create_time']


class BaseModel(HistoryModel):
    """
    the base model contain the status fields of active and delete,contain all the state method
    """
    is_draft = models.BooleanField(
        _('status of draft'),
        blank=False,
        default=True,
        help_text=_('True means instance is draft')
    )

    is_active = models.BooleanField(
        _('status of active'),
        blank=False,
        default=True,
        help_text=_('the status of active,True means active,False means not active')
    )

    class Meta:
        abstract = True

    class States:
        draft = Statement(is_draft=True)
        confirmed = Statement(is_draft=False)
        active = Statement(inherits=confirmed, is_active=True)
        locked = Statement(inherits=confirmed, is_active=False)

    def before_confirm(self):
        pass

    def after_confirm(self):
        pass

    action_confirm = action_factory('draft', to_state='confirmed', name='confirm')

    def before_lock(self):
        pass

    def after_lock(self):
        pass

    action_lock = action_factory('active', to_state='locked', name='lock')

    def before_active(self):
        pass

    def after_active(self):
        pass

    action_active = action_factory('locked', to_state='active', name='active')

    def before_delete(self):
        pass

    def after_delete(self):
        pass

    def action_delete(self, raise_exception=False):
        with transaction.atomic():
            self.check_states('draft', raise_exception=raise_exception)
            self.before_delete()
            self.delete()
            self.after_delete()


class SequenceModel(models.Model):
    """
    the abstract model for data is order by sequence
    """
    sequence = models.PositiveSmallIntegerField(
        _('sequence'),
        null=False,
        blank=True,
        default=1,
        help_text=_("the order of the instance")
    )

    class Meta:
        abstract = True
        ordering = ['sequence']


class DataModel(BaseModel,SequenceModel):
    """
    the abstract model for data can be delete when it is draft,
    and order by sequence defaultly
    """
    class Meta:
        abstract = True
        ordering = ['sequence']


class OrderModel(BaseModel):
    """
    the abstract model that contain the order state
    """
    state = OrderStateCharField(
        _('state'),
        help_text=_("the status of the order")
    )

    class Meta:
        abstract = True

    class States:
        draft = Statement(is_draft=True)
        confirmed = Statement(is_draft=False, state='confirmed')
        active = Statement(inherits=confirmed, is_active=True)
        locked = Statement(inherits=confirmed, is_active=False)
        done = Statement(inherits=locked, state='done')
        cancelled = Statement(inherits=locked, state='cancelled')

    def before_do(self):
        pass

    def after_do(self):
        pass

    action_do = action_factory('acitve', to_state='done', name='do')

    def before_cancel(self):
        pass

    def after_cancel(self):
        pass

    action_cancel = action_factory('confirmed', to_state='cancelled', name='cancel')


class AuditOrderModel(OrderModel):
    """
    the abstract model that can have the audit action
    """

    audit_state = AuditStateCharField(
        _('audit state'),
        help_text=_("the audit state")
    )

    class Meta:
        abstract = True

    class States:
        draft = Statement(is_draft=True)
        confirmed = Statement(is_draft=False, state='confirmed')
        active = Statement(inherits=confirmed, is_active=True)
        locked = Statement(inherits=confirmed, is_active=False)
        auditing = Statement(inherits=active, audit_state='auditing')
        rejected = Statement(inherits=active, audit_state='rejected')
        allowed = Statement(inherits=active, audit_state='allowed')
        done = Statement(inherits=locked, audit_state='allowed', state='done')
        cancelled = Statement(inherits=locked, state='cancelled')

    def before_audit(self):
        pass

    def after_audit(self):
        pass

    action_audit = action_factory('active', 'rejected', to_state='auditing', name='audit')

    def before_reject(self):
        pass

    def after_reject(self):
        pass

    action_reject = action_factory('auditing', to_state='rejected', name='reject')

    def before_allow(self):
        pass

    def after_allow(self):
        pass

    action_allow = action_factory('auditing', to_state='allowed', name='allow')
    action_do = action_factory('allowed', to_state='done', name='do')
