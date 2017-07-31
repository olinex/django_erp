#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from django.db import transaction
from django.db.models import F, Value, Func

from apps.djangoperm import models
from . import state


class BaseModel(models.Model, state.StateMachine):
    is_active = models.BooleanField(
        '可用状态',
        blank=False,
        default=True,
        help_text="记录的可用状态,False为不可用,True为可用"
    )

    is_delete = models.BooleanField(
        '删除状态',
        blank=False,
        default=False,
        help_text="记录的删除状态,True删除不可视,False为尚未删除"
    )

    create_time = models.DateTimeField(
        '创建时间',
        null=False,
        blank=False,
        auto_now_add=True,
        help_text="记录的创建时间,UTC时间"
    )

    last_modify_time = models.DateTimeField(
        '最后修改时间',
        null=False,
        blank=False,
        auto_now=True,
        help_text="记录的最后修改时间,UTC时间"
    )

    class Meta:
        abstract = True

    class States:
        delete = state.Statement(is_delete=True)
        no_delete = state.Statement(is_delete=False)
        active = state.Statement(inherits=no_delete, is_active=True)
        no_active = state.Statement(inherits=no_delete, is_active=False)


class CoordinateModel(models.Model):
    lng = models.DecimalField(
        '经度',
        null=True,
        blank=True,
        max_digits=9,
        decimal_places=6,
        default=None,
        help_text='经度,最大为+180.000000,最小为-180.000000')

    lat = models.DecimalField(
        '纬度',
        null=True,
        blank=True,
        max_digits=9,
        decimal_places=6,
        default=None,
        help_text='纬度,最大为+90.000000,最小为-90.000000')

    class Meta:
        abstract = True

class TreeModel(models.Model):
    index = models.CharField(
        '索引',
        null=False,
        blank=True,
        default='',
        max_length=190,
        help_text="该包裹所在包裹树的索引"
    )

    level = models.PositiveSmallIntegerField(
        '树层',
        null=False,
        blank=False,
        default=0,
        help_text="该包裹所距离所在包裹树的根的距离"
    )

    class Meta:
        abstract = True

    @property
    def root_node(self):
        '''
        获取当前节点的根节点
        :return: PackageNode Instance
        '''
        if self.index != '':
            return self.__class__.objects.get(
                pk=int(self.index.split('-')[0]),
                level=0
            )
        return self

    @property
    def all_child_nodes(self):
        '''
        获取当前节点下所有的子孙节点
        :return: PackageNode Queryset
        '''
        return self.__class__.objects.filter(
            index__startswith='{}{}-'.format(self.index, self.id)
        )

    @property
    def all_parent_nodes(self):
        '''
        获取当前节点的所有父节点
        :return: PackageNode Queryset
        '''
        return self.__class__.objects.filter(
            pk__in=[int(node_pk) for node_pk in self.index.split('-')[:-1]]
        )

    @property
    def sibling_nodes(self):
        '''
        获取当前节点下排除自己的的所有兄弟节点,并排除自身,若为根节点,则返回除了自己之外的所有根节点
        :return: PackageNode Queryset
        '''
        return self.__class__.objects.filter(
            index=self.index,
            level=self.level
        ).exclude(pk=self.pk)

    @property
    @classmethod
    def root_nodes(cls):
        '''
        获取所有根节点
        :return: PackageNode Queryset
        '''
        return cls.objects.filter(
            parent_node=None,
            index='',
            level=0
        )

    def change_parent_node(self, node_pk):
        '''
        修改父节点时,同步更新该节点下的所有子节点key和level
        :node:PackageNode Instance
        :return:True
        '''
        with transaction.atomic():
            node=self.__class__.objects.select_for_update().get(pk=node_pk)
            new_index = '{}{}-'.format(node.index, str(node.pk))
            old_index = self.index
            self.all_child_nodes.select_for_update().update(
                index=Func(F('index'), Value(new_index), Value(old_index), function='replace'),
                level=F('level') + Value(node.level - self.level)
            )
            self.index = new_index
            self.parent_node = node
            self.save()
