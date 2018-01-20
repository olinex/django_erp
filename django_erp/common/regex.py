#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
@author:    olinex
@time:      2018/1/12 下午4:21
"""

DIGIT = r'\d'
NOT_DIGIT = r'\D'
WHITESPACE = r'\s'
NOT_WHITESPACE = r'\S'
ALPHA = r'\w'           # a-z A-Z 0-9 _
NOT_ALPHA = r'\W'

START = r'^'
END = r'$'

# def ITEM(exp):
#     return fr'(?:{exp})'
#
# class REGEX(object):
#
#     def __or__(self, other):
#         return fr'{str(self)}|{other}'
#
#     __xor__ = __or__
#
#     def __mul__(self, other):
#         if isinstance(other,int):
#             return fr'{ITEM(self)}{{{other}}}'
#         if isinstance(other,COUNT):
#             return fr'{ITEM(self)}{other}'
#
# class COUNT(object):
#     _base = ''
#
#     def __init__(self,greedy=True):
#         self.greedy = greedy
#
#     def __str__(self):
#         if self.greedy:
#             return self._base
#         return fr'{self._base}?'
#
#
# class ANY(COUNT):
#     _base = r'*'
#
# class EXIST(COUNT):
#     _base = r'+'
#
# class SINGULAR(COUNT):
#     _base = r'?'
#
# class RANGE(COUNT):
#
#     @property
#     def _base(self):
#         return fr'{{{self.min},{self.max}}}'
#
#     def __init__(self,min=0,max=None,greedy=True):
#         self.min = min
#         self.max = max
#         super(RANGE,self).__init__(greedy)
#
#     def __str__(self):
#         if self.greedy:
#             return self._base
#         return fr'{self._base}?'
#
#
# class INT(REGEX):
#     _base = ITEM(r'[1-9][0-9]*')
#
#     def __init__(self,positive=True,negative=True):
#         self.positive = positive
#         self.negative = negative
#
#     def __str__(self):
#         if self.positive and self.negative:
#             return fr'[+-]?{self._base}'
#         elif self.positive:
#             return fr'+?{self._base}'
#         elif self.negative:
#             return fr'-?{self._base}'
#         else:
#             return self._base
#
# class FLOAT(REGEX):
#     _base = ITEM(fr'[1-9][0-9]*(?:\.[0-9]*)?')
#
#     def __init__(self,positive=True,negative=True):
#         self.positive = positive
#         self.negative = negative
#
#     def __str__(self):
#         if self.positive and self.negative:
#             return fr'[+-]?{self._base}'
#         elif self.positive:
#             return fr'+?{self._base}'
#         elif self.negative:
#             return fr'-?{self._base}'
#         else:
#             return self._base








