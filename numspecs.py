# -*- coding: utf-8 -*-
"""
Created on Fri Apr 12 2018
@name:   NumSpec Objects
@author: Jack Kirby Cook

"""

import re
from numbers import Number

from utilities.quantities import Multiplier, Unit

from specs.spec import Spec, samespec, SpecStringError, SpecValueError, SpecOperationNotSupportedError

__version__ = "1.0.0"
__author__ = "Jack Kirby Cook"
__all__ = ['NumSpec', 'RangeSpec']
__copyright__ = "Copyright 2018, Jack Kirby Cook"
__license__ = ""


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
    @property
    def multiplier(self): return self.__multiplier
    @property
    def unit(self): return self.__unit
    @property
    def numformat(self): return self.__numformat
    @property
    def numstring(self): return self.__numstring
    
    @classmethod
    def setnumformat(self, numformat): self.__numformat = numformat
    
    def __init__(self, *args, multiplier='', unit='', numformat='{:.0f}', numstring='{num}{multi} {unit}', **kwargs): 
        self.__multiplier =  multiplier if isinstance(multiplier, Multiplier) else Multiplier.fromstr(str(multiplier)) 
        self.__unit = unit if isinstance(unit, Unit) else Unit.fromstr(str(unit))     
        self.__numformat, self.__numstring = numformat, numstring
        super().__init__(*args, **kwargs)
        
    def valuestr(self, value): return self.numformat.format(value / self.multiplier.num)
    def numstr(self, value): return self.numstring.format(num=self.valuestr(value), multi=str(self.multiplier), unit=str(self.unit))   
        
    def checkstr(self, string):
        if not len(re.findall(r"[-+]?\d*\.\d+|\d+", string)) == 1: raise SpecStringError(self, string)
    def checkval(self, value): 
        if not isinstance(value, Number): raise SpecValueError(self, value)
    
    def asstr(self, value): 
        return self.numstr(value)     
    def asval(self, string): 
        nums = [num for num in _numfromstr(string)]
        assert len(nums) == 1
        assert isinstance(nums[0], Number)
        return nums[0] * self.multiplier.num
    
    @samespec
    def __eq__(self, other): return self.unit == other.unit
    def todict(self): return dict(data=self.data, datatype=self.datatype, multiplier=str(self.multiplier), unit=str(self.unit), numformat=self.numformat, numstring=self.numstring)

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
    def scale(self, *args, method, axis, **kwargs): return getattr(self, method)(*args, method=method, axis=axis, **kwargs)
    def normalize(self, *args, axis, **kwargs): return self.transformation(*args, method='normalize', axis=axis, multiplier=Multiplier('%'), unit=Unit(), numformat='{:.2f}', numstring='{num}{multi}{unit}', **kwargs)
    def standardize(self, *args, axis, **kwargs): return self.transformation(*args, method='standardize', axis=axis, multiplier=Multiplier(), unit=Unit('σ'), numformat='{:.2f}', numstring='{num}{multi}{unit}', **kwargs)
    def minmax(self, *args, axis, **kwargs): return self.transformation(*args, method='minmax', axis=axis, multiplier=Multiplier('%'), unit=Unit(), numformat='{:.2f}', numstring='{num}{multi}{unit}', **kwargs)
    def group(self, *args, **kwargs): return self.transformation(*args, method='group', datatype='range', **kwargs)

   
@NumSpec.register('range')
class RangeSpec:
    delimiter = ' - '
    headings = {'upper':'>', 'lower':'<', 'center':'', 'state':'', 'unbounded':'...'} 

    def checkstr(self, string): 
        if not bool(string): raise SpecStringError(self, string)
    def checkval(self, value): 
        if not isinstance(value, list): raise SpecValueError(self, value)
        if not len(value) == 2: raise SpecValueError(self, value)
        if not all([isinstance(num, (Number, type(None))) for num in value]): raise SpecValueError(self, value) 
    
    def asstr(self, value):    
        if self.direction(value) == 'state': rangestr = self.numstr(value[0])
        else: rangestr = self.delimiter.join([self.numstr(num) for num in value if num is not None])          
        return self.headings[self.direction(value)] + rangestr
    def asval(self, string):
        nums = [num for num in _numfromstr(string)]
        if self.headings['upper'] in string: nums = [*nums, None]
        elif self.headings['lower'] in string: nums = [None, *nums]
        elif self.headings['unbounded'] in string: nums = [None, None]
        if len(nums) == 1: nums = [*nums, *nums]
        assert len(nums) == 2
        return [num * self.multiplier.num if num is not None else None for num in nums]

    def direction(self, value):
        self.checkval(value)
        lower, upper = value
        if all([x is None for x in value]): return 'unbounded'
        elif lower is None: return 'lower'
        elif upper is None: return 'upper'
        elif lower == upper: return 'state'
        else: return 'center' 
    
    # TRANSFORMATIONS
    def average(self, *args, weight=0.5, **kwargs): 
        assert isinstance(weight, Number)
        assert all([weight <=1, weight >=0])
        return self.transformation(*args, method='average', datatype='num', weight='{:.0f}%wt'.format(weight * 100), **kwargs)    
    
    def cumulate(self, *args, direction, **kwargs): 
        assert direction == 'upper' or direction == 'lower'
        return self.transformation(*args, method='cumulate', datatype='num', direction=direction, **kwargs)    





