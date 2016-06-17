#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-
###############################################################################
#
# Copyright (C) 2015, 2016 Daniel Rodriguez
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import math
import operator

from ..utils.py3 import map, range

from . import Indicator


class PeriodN(Indicator):
    '''
    Base class for indicators which take a period (__init__ has to be called
    either via super or explicitly)

    This class has no defined lines
    '''
    params = (('period', 1),)

    def __init__(self):
        super(PeriodN, self).__init__()
        self.addminperiod(self.p.period)


class OperationN(PeriodN):
    '''
    Calculates "func" for a given period

    Serves as a base for classes that work with a period and can express the
    logic in a callable object

    Note:
      Base classes must provide a "func" attribute which is a callable

    Formula:
      - line = func(data, period)
    '''
    def next(self):
        self.line[0] = self.func(self.data.get(size=self.p.period))

    def once(self, start, end):
        dst = self.line.array
        src = self.data.array
        period = self.p.period
        func = self.func

        for i in range(start, end):
            dst[i] = func(src[i - period + 1: i + 1])


class Highest(OperationN):
    '''
    Calculates the highest value for the data in a given period

    Formula:
      - highest = max(data, period)
    '''
    lines = ('highest',)
    func = max


class Lowest(OperationN):
    '''
    Calculates the lowest value for the data in a given period

    Formula:
      - lowest = min(data, period)
    '''
    lines = ('lowest',)
    func = min


class SumN(OperationN):
    '''
    Calculates the Sum of the data values over a given period

    Formula:
      - sumn = sum(data, period)
    '''
    lines = ('sumn',)
    func = math.fsum


class FindFirstIndex(OperationN):
    '''
    Returns the index of the last data that satisfies equality with the
    condition generated by the parameter _evalfunc

    Note:
      Returned indexes look backwards. 0 is the current index and 1 is
      the previous bar.

    Formula:
      - index = first for which data[index] == _evalfunc(data)
    '''
    lines = ('index',)
    params = (('_evalfunc', None),)

    def func(self, iterable):
        m = self.p._evalfunc(iterable)
        return next(i for i, v in enumerate(reversed(iterable)) if v == m)


class FindFirstIndexHighest(FindFirstIndex):
    '''
    Returns the index of the first data that is the highest in the period

    Note:
      Returned indexes look backwards. 0 is the current index and 1 is
      the previous bar.

    Formula:
      - index = index of first data which is the highest
    '''
    params = (('_evalfunc', max),)


class FindFirstIndexLowest(FindFirstIndex):
    '''
    Returns the index of the first data that is the lowest in the period

    Note:
      Returned indexes look backwards. 0 is the current index and 1 is
      the previous bar.

    Formula:
      - index = index of first data which is the lowest
    '''
    params = (('_evalfunc', min),)


class FindLastIndex(OperationN):
    '''
    Returns the index of the last data that satisfies equality with the
    condition generated by the parameter _evalfunc

    Note:
      Returned indexes look backwards. 0 is the current index and 1 is
      the previous bar.

    Formula:
      - index = last for which data[index] == _evalfunc(data)
    '''
    lines = ('index',)
    params = (('_evalfunc', None),)

    def func(self, iterable):
        m = self.p._evalfunc(iterable)
        index = next(i for i, v in enumerate(iterable) if v == m)
        # The iterable goes from 0 -> period - 1. If the last element
        # which is the current bar is returned and without the -1 then
        # period - index = 1 ... and must be zero!
        return self.p.period - index - 1


class FindLastIndexHighest(FindLastIndex):
    '''
    Returns the index of the last data that is the highest in the period

    Note:
      Returned indexes look backwards. 0 is the current index and 1 is
      the previous bar.

    Formula:
      - index = index of last data which is the highest
    '''
    params = (('_evalfunc', max),)


class FindLastIndexLowest(FindLastIndex):
    '''
    Returns the index of the last data that is the lowest in the period

    Note:
      Returned indexes look backwards. 0 is the current index and 1 is
      the previous bar.

    Formula:
      - index = index of last data which is the lowest
    '''
    params = (('_evalfunc', min),)


class Accum(Indicator):
    '''
    Cummulative sum of the data values

    Formula:
      - accum += data
    '''
    alias = ('CumSum', 'CumulativeSum',)
    lines = ('accum',)
    params = (('seed', 0.0),)

    # xxxstart methods use the seed (starting value) and passed data to
    # construct the first value keeping the minperiod to 1 since no
    # initial look-back value is needed

    def nextstart(self):
        self.line[0] = self.p.seed + self.data[0]

    def next(self):
        self.line[0] = self.line[-1] + self.data[0]

    def oncestart(self, start, end):
        dst = self.line.array
        src = self.data.array
        prev = self.p.seed

        for i in range(start, end):
            dst[i] = prev = prev + src[i]

    def once(self, start, end):
        dst = self.line.array
        src = self.data.array
        prev = dst[start - 1]

        for i in range(start, end):
            dst[i] = prev = prev + src[i]


class Average(PeriodN):
    '''
    Averages a given data arithmetically over a period

    Formula:
      - av = data(period) / period

    See also:
      - https://en.wikipedia.org/wiki/Arithmetic_mean
    '''
    alias = ('ArithmeticMean', 'Mean',)
    lines = ('av',)

    def next(self):
        self.line[0] = \
            math.fsum(self.data.get(size=self.p.period)) / self.p.period

    def once(self, start, end):
        src = self.data.array
        dst = self.line.array
        period = self.p.period

        for i in range(start, end):
            dst[i] = math.fsum(src[i - period + 1:i + 1]) / period


class ExponentialSmoothing(Average):
    '''
    Averages a given data over a period using exponential smoothing

    A regular ArithmeticMean (Average) is used as the seed value considering
    the first period values of data

    Formula:
      - av = prev * (1 - alpha) + data * alpha

    See also:
      - https://en.wikipedia.org/wiki/Exponential_smoothing
    '''
    alias = ('ExpSmoothing',)
    params = (('alpha', None),)

    def __init__(self):
        self.alpha = self.p.alpha
        self.alpha1 = 1.0 - self.p.alpha
        super(ExponentialSmoothing, self).__init__()

    def nextstart(self):
        # Fetch the seed value from the base class calculation
        super(ExponentialSmoothing, self).next()

    def next(self):
        self.line[0] = self.line[-1] * self.alpha1 + self.data[0] * self.alpha

    def oncestart(self, start, end):
        # Fetch the seed value from the base class calculation
        super(ExponentialSmoothing, self).once(start, end)

    def once(self, start, end):
        darray = self.data.array
        larray = self.line.array
        alpha = self.alpha
        alpha1 = self.alpha1

        # Seed value from SMA calculated with the call to oncestart
        prev = larray[start - 1]
        for i in range(start, end):
            larray[i] = prev = prev * alpha1 + darray[i] * alpha


class ExponentialSmoothingDynamic(ExponentialSmoothing):
    '''
    Averages a given data over a period using exponential smoothing

    A regular ArithmeticMean (Average) is used as the seed value considering
    the first period values of data

    Note:
      - alpha is an array of values which can be calculated dynamically

    Formula:
      - av = prev * (1 - alpha) + data * alpha

    See also:
      - https://en.wikipedia.org/wiki/Exponential_smoothing
    '''
    alias = ('ExpSmoothingDynamic',)

    def __init__(self):
        super(ExponentialSmoothingDynamic, self).__init__()

        # Hack: alpha is a "line" and carries a minperiod which is not being
        # considered because this indicator makes no line assignment. It has
        # therefore to be considered manually
        minperioddiff = max(0, self.alpha._minperiod - self.p.period)
        self.lines[0].incminperiod(minperioddiff)

    def next(self):
        self.line[0] = \
            self.line[-1] * self.alpha1[0] + self.data[0] * self.alpha[0]

    def once(self, start, end):
        darray = self.data.array
        larray = self.line.array
        alpha = self.alpha.array
        alpha1 = self.alpha1.array

        # Seed value from SMA calculated with the call to oncestart
        prev = larray[start - 1]
        for i in range(start, end):
            larray[i] = prev = prev * alpha1[i] + darray[i] * alpha[i]


class WeightedAverage(PeriodN):
    '''
    Calculates the weighted average of the given data over a period

    The default weights (if none are provided) are linear to assigne more
    weight to the most recent data

    The result will be multiplied by a given "coef"

    Formula:
      - av = coef * sum(mul(data, period), weights)

    See:
      - https://en.wikipedia.org/wiki/Weighted_arithmetic_mean
    '''
    alias = ('AverageWeighted',)
    lines = ('av',)
    params = (('coef', 1.0), ('weights', tuple()),)

    def __init__(self):
        super(WeightedAverage, self).__init__()

    def next(self):
        data = self.data.get(size=self.p.period)
        dataweighted = map(operator.mul, data, self.p.weights)
        self.line[0] = self.p.coef * math.fsum(dataweighted)

    def once(self, start, end):
        darray = self.data.array
        larray = self.line.array
        period = self.p.period
        coef = self.p.coef
        weights = self.p.weights

        for i in range(start, end):
            data = darray[i - period + 1: i + 1]
            larray[i] = coef * math.fsum(map(operator.mul, data, weights))
