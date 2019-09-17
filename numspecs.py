# -*- coding: utf-8 -*-
"""
Created on Fri Apr 12 2018
@name:   NumSpec Objects
@author: Jack Kirby Cook

"""

import re
from numbers import Number
from functools import update_wrapper

from utilities.quantities import Multiplier, Unit, Heading
from utilities.dispatchers import clskey_singledispatcher as keydispatcher

from specs.spec import Spec, SpecStringError, SpecValueError, SpecOperationNotSupportedError

__version__ = "1.0.0"
__author__ = "Jack Kirby Cook"
__all__ = ['NumSpec', 'RangeSpec']
__copyright__ = "Copyright 2018, Jack Kirby Cook"
__license__ = ""


_INF = '∞'
_ALL = '*'
_DELIMITER = '|'

_NUMFORMAT = 'num:.{precision}f'
_NUMSTRFORMAT = '{numdirection}{heading}{numstr}{multiplier}{unit}'
_DIRECTIONS = {'upper':'>', 'lower':'<', 'state':'', 'unbounded':_ALL, 'center':''}
_NUMDIRECTIONS = {'upper':'▲', 'lower':'▼', 'state':''}
_DEFAULTS = {'numdirection':'state', 'heading':'', 'precision':0, 'unit':'', 'multiplier':''}

_aslist = lambda items: [items] if not isinstance(items, (list, tuple)) else list(items)
_fixnumtype = lambda num: None if num is None else int(float(num)) if not bool(float(num) % 1) else float(num)


def _numfromstr(numstr): 
    nums = re.findall(r"[-+]?\d*\.\d+|\d+", numstr)
    if len(nums) == 0: 
        yield None
    elif len(nums) == 1: 
        yield _fixnumtype(nums[0])
    else: 
        for num in nums: yield _fixnumtype(num)

def _numformatting(num, *args, precision, nummultiplier, **kwargs):
    assert isinstance(num, Number)
    assert isinstance(precision, int)
    assert isinstance(nummultiplier, Number)
    numformat = '{' + _NUMFORMAT.format(precision=precision) + '}'
    return numformat.format(num=num/nummultiplier)
    
def _numstrformatting(num, *args, heading, multiplier, unit, numdirection, **kwargs):
    assert isinstance(multiplier, Multiplier)
    assert isinstance(unit, Unit)
    assert isinstance(heading, Heading)
    if num is None: return _ALL
    numstr = _numformatting(num, *args, nummultiplier=multiplier.num, **kwargs)
    return _NUMSTRFORMAT.format(numstr=numstr, heading=str(heading), multiplier=str(multiplier), unit=str(unit), numdirection=_NUMDIRECTIONS[numdirection], **kwargs)

def _rangestrformatting(lowernum, uppernum, *args, **kwargs):
    return _DELIMITER.join([_numformatting(lowernum, *args, **kwargs), _numformatting(uppernum, *args, **kwargs)])


def _formatting(function):
    def wrapper(*args, formatting={}, **kwargs):
        kwargs.update(formatting)
        return function(*args, **kwargs)
    update_wrapper(wrapper, function)
    return wrapper


@Spec.register('num')
class NumSpec:  
    @property
    def heading(self): return self.__heading    
    @property
    def numdirection(self): return self.__numdirection    
    @property
    def multiplier(self): return self.__multiplier
    @property
    def unit(self): return self.__unit
    @property
    def precision(self): return self.__precision
    
    def __init__(self, *args, numdirection, heading, precision, multiplier, unit, **kwargs): 
        assert numdirection in _NUMDIRECTIONS.keys()    
        self.__heading = heading if isinstance(heading, Heading) else Heading.fromstr(str(heading)) 
        self.__multiplier =  multiplier if isinstance(multiplier, Multiplier) else Multiplier.fromstr(str(multiplier)) 
        self.__unit = unit if isinstance(unit, Unit) else Unit.fromstr(str(unit)) 
        self.__precision = int(precision)
        self.__numdirection = numdirection             
        super().__init__(*args, **kwargs)
        
    def checkstr(self, string):
        if not len(re.findall(r"[-+]?\d*\.\d+|\d+", string)) == 1 and not _ALL in string: raise SpecStringError(self, string)
    
    def checkval(self, value): 
        if not isinstance(value, Number): raise SpecValueError(self, value)
    
    def asstr(self, value): 
        self.checkval(value)
        return _numstrformatting(value, **self.todict())     
   
    def asval(self, string): 
        self.checkstr(string)
        num = [num for num in _numfromstr(string)][0]
        return num * self.multiplier.num if num is not None else None

    def __eq__(self, other): return self.unit == other.unit
    def todict(self): return dict(**super().todict(), multiplier=self.multiplier, unit=self.unit, heading=self.heading, precision=self.precision, numdirection=self.numdirection)

    # OPERATIONS
    def add(self, other, *args, **kwargs): return self.operation(other, *args, method='add', **kwargs)
    def subtract(self, other, *args, **kwargs): return self.operation(other, *args, method='subtract', **kwargs)

    @_formatting
    def multiply(self, other, *args, **kwargs): 
        if type(other) != NumSpec: raise SpecOperationNotSupportedError(self, other, 'multiply') 
        heading = kwargs.get('heading', self.heading * other.heading)   
        unit = self.unit * other.unit                    
        return self.operation(other, *args, method='multiply', heading=heading, unit=unit, **kwargs) 
        
    @_formatting
    def divide(self, other, *args, **kwargs): 
        if type(other) != NumSpec: raise SpecOperationNotSupportedError(self, other, 'divide') 
        heading = kwargs.get('heading', self.heading / other.heading)
        unit = self.unit / other.unit             
        return self.operation(other, *args, method='divide', heading=heading, unit=unit, **kwargs) 
       
    # TRANSFORMATIONS    
    @keydispatcher('how')
    def moving(self, *args, how, **kwargs): raise KeyError(how)
    @moving.register('average')
    def __average(self, *args, how, **kwargs): return self.transformation(*args, method='moving', how='average', numdirection='state', **kwargs)
    @moving.register('total')
    def __total(self, *args, how, **kwargs): return self.transformation(*args, method='moving', how='total', numdirection='state', **kwargs)
    @moving.register('bracket')
    def __bracket(self, *args, how, **kwargs): return self.transformation(*args, datatype='range', method='moving', how='bracket', numdirection='state', **kwargs)
    @moving.register('differential')
    def __differential(self, *args, how, **kwargs): return self.transformation(*args, method='moving', how='differential', numdirection='state', **kwargs)
    
    @keydispatcher('how')
    def scale(self, *args, how, along, **kwargs): raise KeyError(how)
    @scale.register('normalize')
    def __normalize(self, *args, how, axis, **kwargs): return self.transformation(*args, method='scale', how='normalize', unit='', multiplier='%', axis=axis, **kwargs)
    @scale.register('standardize')
    def __standardize(self, *args, how, axis, **kwargs): return self.transformation(*args, method='scale', how='standardize', unit='σ', multiplier='', axis=axis, **kwargs)
    @scale.register('minmax')
    def __minmax(self, *args, how, axis, **kwargs): return self.transformation(*args, method='scale', how='minmax', unit='', multiplier='%', axis=axis, **kwargs)    
    
    @keydispatcher('how')
    def unconsolidate(self, *args, how, **kwargs): raise KeyError(how)
    @unconsolidate.register('uncumulate')
    def __uncumulate(self, *args, how, direction, **kwargs): 
        assert direction == 'lower' or direction == 'upper'
        assert direction == self.numdirection
        return self.transformation(*args, datatype='range', method='unconsolidate', how='uncumulate', numdirection='state', **kwargs)
    @unconsolidate.register('group')
    def __group(self, *args, how, **kwargs): return self.transformation(*args, datatype='range', method='unconsolidate', how='group', numdirection='state', **kwargs)
    
    @keydispatcher('how')
    def factor(self, *args, how, factor, **kwargs): raise KeyError(how)
    @factor.register('multiply')
    @_formatting
    def __multiply(self, *args, how, factor, **kwargs): 
        return self.transformation(*args, method='factor', how='multiply', factor=factor, **kwargs)
    @factor.register('divide')
    @_formatting
    def __divide(self, *args, how, factor, **kwargs): 
        return self.transformation(*args, method='factor', how='divide', factor=factor, **kwargs)

    @classmethod
    def fromfile(cls, *args, databasis={}, **kwargs):
        assert isinstance(databasis, dict)
        formatting = {key:databasis.pop(key, value) for key, value in _DEFAULTS.items()}
        return cls(*args, **formatting, **kwargs)
        
   
@NumSpec.register('range')
class RangeSpec:
    def direction(self, value):
        self.checkval(value)
        lowernum, uppernum = value
        if all([x is None for x in value]): return 'unbounded'
        elif lowernum is None: return 'lower'
        elif uppernum is None: return 'upper'
        elif lowernum == uppernum: return 'state'
        else: return 'center' 

    def checkstr(self, string): 
        if not bool(string): raise SpecStringError(self, string)
    
    def checkval(self, value): 
        if not isinstance(value, list): raise SpecValueError(self, value)
        if not len(value) == 2: raise SpecValueError(self, value)
        if not all([isinstance(num, (Number, type(None))) for num in value]): raise SpecValueError(self, value) 
        if None not in value: 
            if value[0] > value[-1]: raise SpecValueError(self, value)
    
    def asstr(self, value):   
        self.checkval(value)
        if self.direction(value) == 'state': rangestr = _numstrformatting(value[0], **self.todict())    
        else: rangestr = _DELIMITER.join([_numstrformatting(num, **self.todict()) for num in value if num is not None])   
        return _DIRECTIONS[self.direction(value)] + rangestr
    
    def asval(self, string):
        self.checkstr(string)
        nums = [num for num in _numfromstr(string)]
        if _DIRECTIONS['upper'] in string: nums = [*nums, None]
        elif _DIRECTIONS['lower'] in string: nums = [None, *nums]
        elif _DIRECTIONS['unbounded'] in string: nums = [None, None]
        if len(nums) == 1: nums = [*nums, *nums]
        assert len(nums) == 2
        if None not in nums: nums = [min(nums), max(nums)]
        return [num * self.multiplier.num if num is not None else None for num in nums]
   
    # TRANSFORMATIONS    
    @keydispatcher('how')
    def consolidate(self, *args, how, **kwargs): raise KeyError(how)
    
    @consolidate.register('average')
    def __average(self, *args, how, weight=0.5, **kwargs): 
        assert isinstance(weight, Number)
        assert all([weight <=1, weight >=0])
        return self.transformation(*args, datatype='num', method='consolidate', how='average', weight='{:.0f}%'.format(weight * 100), **kwargs)    
    
    @consolidate.register('cumulate')
    def __cumulate(self, *args, how, direction, **kwargs): 
        assert direction == 'upper' or direction == 'lower'
        return self.transformation(*args, datatype='num', method='consolidate', how='cumulate', direction=direction, numdirection=direction, **kwargs)    

    @consolidate.register('differential')
    def __differential(self, *args, how, **kwargs):
        return self.transformation(*args, datatype='num', method='consolidate', how='differential', **kwargs)

    def unconsolidate(self, *args, **kwargs): raise NotImplementedError('{}.{}()'.format(self.__class__.__name__, 'unconsolidate'))














