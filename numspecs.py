# -*- coding: utf-8 -*-
"""
Created on Fri Apr 12 2018
@name:   NumSpec Objects
@author: Jack Kirby Cook

"""

import re
from numbers import Number

from utilities.quantities import Multiplier, Unit
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
_MULTIPLYFORMATTING = {'multiplier':'', 'precision':0}
_DIVIDEFORMATTING = {'multiplier':'', 'precision':3}
_NORMFORMATTING = {'multiplier':'%', 'precision':2}
_STDEVFORMATTING = {'multiplier':'', 'precision':2}
_MINMAXFORMATTING = {'multiplier':'%', 'precision':2}
_DEFAULTS = {'unit':'', 'multiplier':'', 'precision':0, 'numdirection':'state', 'heading':''}


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
    if num is None: return _ALL
    numstr = _numformatting(num, *args, nummultiplier=multiplier.num, **kwargs)
    return _NUMSTRFORMAT.format(numstr=numstr, heading=heading, multiplier=str(multiplier), unit=str(unit), numdirection=_NUMDIRECTIONS[numdirection], **kwargs)

def _rangestrformatting(lowernum, uppernum, *args, **kwargs):
    return _DELIMITER.join([_numformatting(lowernum, *args, **kwargs), _numformatting(uppernum, *args, **kwargs)])


def num_adapter(function):
    def wrapper(self, *args, databasis={}, formatting={}, **kwargs):
        assert isinstance(databasis, dict)
        assert isinstance(formatting, dict)
        getvalue = lambda key, default: formatting.get(key, databasis.get(key, kwargs.get(key, default)))    

        unit, multiplier = [getvalue(key, _DEFAULTS[key]) for key in ('unit', 'multiplier')]
        precision = int(getvalue('precision', _DEFAULTS['precision']))
        heading, numdirection = [getvalue(key, _DEFAULTS[key]) for key in ('heading', 'numdirection')]
        
        multiplier =  multiplier if isinstance(multiplier, Multiplier) else Multiplier.fromstr(str(multiplier)) 
        unit = unit if isinstance(unit, Unit) else Unit.fromstr(str(unit))
        function(self, *args, unit=unit, heading=heading, numdirection=numdirection, multiplier=multiplier, precision=precision, **kwargs)
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
    
    @num_adapter
    def __init__(self, *args, unit, heading, numdirection, multiplier, precision, **kwargs): 
        assert numdirection in _NUMDIRECTIONS.keys()    
        self.__multiplier =  multiplier 
        self.__unit = unit 
        self.__precision = precision
        self.__numdirection = numdirection     
        self.__heading = heading
        super().__init__(*args, **kwargs)
        
    def checkstr(self, string):
        if not len(re.findall(r"[-+]?\d*\.\d+|\d+", string)) == 1 and not _ALL in string: raise SpecStringError(self, string)
    
    def checkval(self, value): 
        if not isinstance(value, (Number, type(None))): raise SpecValueError(self, value)
    
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

    def multiply(self, other, *args, **kwargs): 
        if type(other) != NumSpec: raise SpecOperationNotSupportedError(self, other, 'multiply') 
        unit = self.unit * other.unit        
        precision = kwargs.get('precision', _MULTIPLYFORMATTING['precision'])  
        multiplier = kwargs.get('multiplier', self.multiplier * other.multiplier)                 
        return self.operation(other, *args, method='multiply', unit=unit, multiplier=multiplier, precision=precision, **kwargs) 
        
    def divide(self, other, *args, **kwargs): 
        if type(other) != NumSpec: raise SpecOperationNotSupportedError(self, other, 'divide') 
        unit = self.unit / other.unit        
        precision = kwargs.get('precision', _DIVIDEFORMATTING['precision'])   
        multiplier = kwargs.get('multiplier', self.multiplier / other.multiplier)               
        return self.operation(other, *args, method='multiply', unit=unit, multiplier=multiplier, precision=precision, **kwargs) 
       
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
    def __normalize(self, *args, how, axis, **kwargs): return self.transformation(*args, method='scale', how='normalize', unit=Unit(), **_NORMFORMATTING, axis=axis, **kwargs)
    @scale.register('standardize')
    def __standardize(self, *args, how, axis, **kwargs): return self.transformation(*args, method='scale', how='standardize', unit=Unit('σ'), **_STDEVFORMATTING, axis=axis, **kwargs)
    @scale.register('minmax')
    def __minmax(self, *args, how, axis, **kwargs): return self.transformation(*args, method='scale', how='minmax', unit=Unit(), axis=axis, **_MINMAXFORMATTING, **kwargs)    
    
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
    def __multiply(self, *args, how, factor, **kwargs): 
        precision = kwargs.get('precision', _MULTIPLYFORMATTING['precision'])  
        multiplier = kwargs.get('multiplier', _MULTIPLYFORMATTING['multiplier'])       
        return self.transformation(*args, method='factor', how='multiply', factor=factor, multiplier=multiplier, precision=precision, **kwargs)
    @factor.register('divide')
    def __divide(self, *args, how, factor, **kwargs): 
        precision = kwargs.get('precision', _DIVIDEFORMATTING['precision'])  
        multiplier = kwargs.get('multiplier', _DIVIDEFORMATTING['multiplier'])         
        return self.transformation(*args, method='factor', how='divide', factor=factor, multiplier=multiplier, precision=precision, **kwargs)
   
@NumSpec.register('range')
class RangeSpec:
    def direction(self, value):
        self.checkval(value)
        lower, upper = value
        if all([x is None for x in value]): return 'unbounded'
        elif lower is None: return 'lower'
        elif upper is None: return 'upper'
        elif lower == upper: return 'state'
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

    def unconsolidate(self, *args, **kwargs): raise NotImplementedError('{}.{}()'.format(self.__class__.__name__, 'unconsolidate'))














