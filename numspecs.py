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

from specs.spec import Spec, samespec, SpecStringError, SpecValueError, SpecOperationNotSupportedError

__version__ = "1.0.0"
__author__ = "Jack Kirby Cook"
__all__ = ['NumSpec', 'RangeSpec']
__copyright__ = "Copyright 2018, Jack Kirby Cook"
__license__ = ""


_INF = '∞'
_aslist = lambda items: [items] if not isinstance(items, (list, tuple)) else list(items)
_fixnumtype = lambda num: None if num is None else int(float(num)) if not bool(float(num) % 1) else float(num)

def _numfromstr(numstr): 
    nums = re.findall(r"[-+]?\d*\.\d+|\d+", numstr)
    if len(nums) == 0: yield None
    elif len(nums) == 1: yield _fixnumtype(nums[0])
    else: 
        for num in nums: yield _fixnumtype(num)


@Spec.register('num')
class NumSpec:  
    numdirections = {'upper':"▲", 'lower':"▼", 'state':""}
    
    @property
    def multiplier(self): return self.__multiplier
    @property
    def unit(self): return self.__unit
    @property
    def numformat(self): return self.__numformat
    @property
    def numstring(self): return self.__numstring
    @property
    def numdirection(self): return self.__numdirection
    
    @classmethod
    def setnumformat(self, numformat): self.__numformat = numformat
    
    def __init__(self, *args, multiplier='', unit='', numformat='{:.0f}', numstring='{drt}{num}{multi} {unit}', numdirection='state', **kwargs): 
        assert numdirection in self.numdirections.keys()
        self.__multiplier =  multiplier if isinstance(multiplier, Multiplier) else Multiplier.fromstr(str(multiplier)) 
        self.__unit = unit if isinstance(unit, Unit) else Unit.fromstr(str(unit))     
        self.__numformat, self.__numstring = numformat, numstring
        self.__numdirection = numdirection
        super().__init__(*args, **kwargs)
        
    def valuestr(self, value): return self.numformat.format(value / self.multiplier.num)
    def numstr(self, value): return self.numstring.format(num=self.valuestr(value), multi=str(self.multiplier), unit=str(self.unit), drt=self.numdirections[self.numdirection])   
        
    def checkstr(self, string):
        if not len(re.findall(r"[-+]?\d*\.\d+|\d+", string)) == 1: raise SpecStringError(self, string)
    
    def checkval(self, value): 
        if not isinstance(value, (Number, type(None))): raise SpecValueError(self, value)
    
    def asstr(self, value): 
        return self.numstr(value)     
    
    def asval(self, string): 
        nums = [num for num in _numfromstr(string)]
        assert len(nums) == 1
        assert isinstance(nums[0], Number)
        return nums[0] * self.multiplier.num
    
    @samespec
    def __eq__(self, other): return self.unit == other.unit
    def todict(self): return dict(**super().todict(), multiplier=str(self.multiplier), unit=str(self.unit), numformat=self.numformat, numstring=self.numstring, numdirection=self.numdirection)

    # OPERATIONS
    @samespec
    def add(self, other, *args, **kwargs): return self.operation(other, *args, method='add', **kwargs)
    @samespec
    def subtract(self, other, *args, **kwargs): return self.operation(other, *args, method='subtract', **kwargs)

    def multiply(self, other, *args, **kwargs): 
        if type(other) != NumSpec: raise SpecOperationNotSupportedError(self, other, 'multiply') 
        unit = self.unit * other.unit
        multiplier = self.multiplier * other.multiplier  
        numformat = kwargs.get('numformat', '{:.0f}')
        numstring = kwargs.get('numstring', self.numstring)
        return self.operation(other, *args, method='multiply', multiplier=multiplier, unit=unit, numformat=numformat, numstring=numstring, **kwargs) 
        
    def divide(self, other, *args, **kwargs): 
        if type(other) != NumSpec: raise SpecOperationNotSupportedError(self, other, 'divide') 
        unit = self.unit / other.unit
        multiplier = self.multiplier / other.multiplier        
        numformat = kwargs.get('numformat', '{:.2f}')
        numstring = kwargs.get('numstring', self.numstring) 
        return self.operation(other, *args, method='divide', multiplier=multiplier, unit=unit, numformat=numformat, numstring=numstring, **kwargs) 

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
    def scale(self, *args, how, **kwargs): raise KeyError(how)
    @scale.register('normalize')
    def __normalize(self, *args, how, **kwargs): return self.transformation(*args, method='scale', how='normalize', multiplier=Multiplier('%'), unit=Unit(), numformat='{:.2f}', numstring='{drt}{num}{multi}{unit}', **kwargs)
    @scale.register('standardize')
    def __standardize(self, *args, how, **kwargs): return self.transformation(*args, method='scale', how='standardize', multiplier=Multiplier(), unit=Unit('σ'), numformat='{:.2f}', numstring='{drt}{num}{multi}{unit}', **kwargs)
    @scale.register('minmax')
    def __minmax(self, *args, how, **kwargs): return self.transformation(*args, method='scale', how='minmax', multiplier=Multiplier('%'), unit=Unit(), numformat='{:.2f}', numstring='{drt}{num}{multi}{unit}', **kwargs)    
    
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
    def __multiply(self, *args, how, factor, **kwargs): return self.transformation(*args, method='factor', how='multiply', factor=factor, **kwargs)
    @factor.register('divide')
    def __divide(self, *args, how, factor, **kwargs): return self.transformation(*args, method='factor', how='multiply', factor=factor, **kwargs)

    
   
@NumSpec.register('range')
class RangeSpec:
    delimiter = ' - '
    directions = {'upper':'>', 'lower':'<', 'state':'', 'unbounded':'...', 'center':''}

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
        if self.direction(value) == 'state': rangestr = self.numstr(value[0])
        rangestr = self.delimiter.join([self.numstr(num) for num in value if num is not None])   
        return self.directions[self.direction(value)] + rangestr
    
    def asval(self, string):
        nums = [num for num in _numfromstr(string)]
        if self.directions['upper'] in string: nums = [*nums, None]
        elif self.directions['lower'] in string: nums = [None, *nums]
        elif self.directions['unbounded'] in string: nums = [None, None]
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














