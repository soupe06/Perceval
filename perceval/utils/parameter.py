# MIT License
#
# Copyright (c) 2022 Quandela
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import random
import sympy as sp
from .format import simple_float

from typing import Tuple


class Parameter:
    r"""A Parameter is a used as a variable in a circuit definition

    Parameters are a simple way to introduce named variables in a circuit. They take floating number values. When non
    defined they are associated to sympy symbols and will be used to perform symbolic calculations.

    :param name: name of the parameter
    :param value: optional value, when the value is provided at initialization, the parameter is considered as `fixed`
    :param min_v: minimal value that the parameter can take, is used in circuit optimization
    :param max_v: maximal value that the parameter can take, is used in circuit optimization
    """
    _id = 0

    def __init__(self, name: str, value: float = None, min_v: float = None, max_v: float = None, periodic=True):
        if min_v is not None:
            self._min = float(min_v)
        else:
            self._min = None
        if max_v is not None:
            self._max = float(max_v)
        else:
            self._max = None
        if value is None:
            self._symbol = sp.symbols(name, real=True)
            self._value = None
        else:
            if not isinstance(value, sp.Expr):
                self._value = self._check_value(value, self._min, self._max, periodic)
            else:
                self._value = value
            self._symbol = None
        self.name = name
        self._periodic = periodic
        self._pid = Parameter._id
        Parameter._id += 1

    @property
    def spv(self) -> sp.Expr:
        r"""The current value of the parameter defined as a sympy expression
        """
        if self._value is not None:
            return sp.S(self._value)
        else:
            return self._symbol

    def __float__(self):
        r"""Convert the parameter to float, will fail if the parameter has no defined value
        """
        return float(self._value)

    def random(self):
        if self._symbol is None:
            return float(self._value)
        if self._min is not None and self._max is not None:
            return float(random.random() * (self._max-self._min) + self._min)
        return random.random()

    @staticmethod
    def _check_value(v: float, min_v: float, max_v: float, periodic: bool):
        if periodic and min_v is not None and max_v is not None:
            if v > max_v:
                p = int((v-max_v)/(max_v-min_v))
                v = v - (p+1) * (max_v-min_v)
            elif v < min_v:
                p = int((min_v-v)/(max_v-min_v))
                v = v + (p+1) * (max_v-min_v)
        if (min_v is not None and v < min_v) or (max_v is not None and v > max_v):
            raise ValueError("value %f out of bound [%f,%f]", v, min_v, max_v)
        return v

    def set_value(self, v: float):
        r"""Define the value of a non-fixed parameter

        :param v: the value
        :raise: `RuntimeError` if the parameter is fixed
        """
        if self.fixed:
            raise RuntimeError("cannot set fixed parameter")
        self._value = self._check_value(v, self._min, self._max, self._periodic)

    def fix_value(self, v):
        r"""Fix the value of a non-fixed parameter

        :param v: the value
        """
        self._symbol = None
        self._value = self._check_value(v, self._min, self._max, self._periodic)

    @property
    def defined(self) -> bool:
        r"""Return True if the parameter has a value (fixed or non fixed)
        """
        return self._value is not None

    @property
    def is_periodic(self) -> bool:
        r"""Return True if the parameter is defined as a period parameter
        """
        return self._periodic

    def set_periodic(self, periodic):
        r"""set periodic flag"""
        self._periodic = periodic

    @property
    def fixed(self) -> bool:
        r"""Return True if the parameter is fixed
        """
        return self._symbol is None

    def __repr__(self):
        return "Parameter(name='%s', value=%s%s%s)" % (str(self.name), str(self._value),
                                                       self._min is not None and ", min="+str(self._min) or "",
                                                       self._max is not None and ", max="+str(self._max) or "")

    @property
    def bounds(self) -> Tuple[float, float]:
        r"""Minimal and maximal values for the parameter
        """
        return (self._min, self._max)

    @property
    def min(self):
        r"""The minimal value of the parameter
        """
        return self._min

    @min.setter
    def min(self, m: float):
        r"""Set the minimal value of the parameter
        """
        self._min = m

    @property
    def max(self) -> float:
        r"""The maximal value of the parameter

        """
        return self._max

    @max.setter
    def max(self, m: bool):
        r"""Set the maximal value of the parameter

        """
        self._max = m

    @property
    def pid(self):
        r"""Unique identifier for the parameter"""
        return self._pid


P = Parameter
