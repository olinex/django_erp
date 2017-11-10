#!/usr/bin/env python3
# -*- coding:utf-8 -*-


from common.rest.viewsets import BaseViewSet, PermMethodViewSet
from .. import models
from .. import serializers
from .. import filters


class ProvinceViewSet(PermMethodViewSet):
    model = models.Province
    allow_actions = ('create', 'list', 'retrieve', 'update')
    serializer_class = serializers.ProvinceSerializer
    filter_class = filters.ProvinceFilter


class CityViewSet(PermMethodViewSet):
    model = models.City
    allow_actions = ('create', 'list', 'retrieve', 'update')
    serializer_class = serializers.CitySerializer


class RegionViewSet(PermMethodViewSet):
    model = models.Region
    allow_actions = ('create', 'list', 'retrieve', 'update')
    serializer_class = serializers.RegionSerializer


class AddressViewSet(BaseViewSet):
    model = models.Address
    serializer_class = serializers.AddressSerializer
