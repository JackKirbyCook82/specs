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


normalize_data = lambda data: '({})'.format('_'.join(['quantiles', data]))
standardize_data = lambda data: '({})'.format('_'.join(['zscores', data]))
minmax_data = lambda data: '({})'.format('_'.join(['minmax', data]))
average_data = lambda weight, data: '({})'.format('{:.0f}%wt|avg_{}'.format(weight * 100, data))
cumulate_data = lambda direction, data: '({})'.format('{}|cum_{}'.format(direction, data))
group_data = lambda data: '({})'.format('_'.join(['bins', data]))


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
    def add(self, other, *args, **kwargs): return self
    @samespec
    def subtract(self, other, *args, **kwargs): return self

    def multiply(self, other, *args, **kwargs): 
        if type(other) != NumSpec: raise SpecOperationNotSupportedError(self, other, 'multiply')
        data = kwargs.get('data', '*'.join([self.data, other.data]))  
        unit = self.unit * other.unit
        multiplier = self.multiplier * other.multiplier  
        numformat = kwargs.get('numformat', '{:.0f}')
        numstring = kwargs.get('numstring', self.numstring)
        return self.__class__(data=data, multiplier=multiplier, unit=unit, numformat=numformat, numstring=numstring)
        
    def divide(self, other, *args, **kwargs): 
        if type(other) != NumSpec: raise SpecOperationNotSupportedError(self, other, 'multiply')
        data = kwargs.get('data', '/'.join([self.data, other.data]))  
        unit = self.unit / other.unit
        multiplier = self.multiplier / other.multiplier        
        numformat = kwargs.get('numformat', '{:.2f}')
        numstring = kwargs.get('numstring', self.numstring) 
        return self.__class__(data=data, multiplier=multiplier, unit=unit, numformat=numformat, numstring=numstring)

    # TRANSFORMATIONS
    def normalize(self, *args, **kwargs): return self.__class__(data=normalize_data(self.data), multiplier=Multiplier('%'), unit=Unit(), numformat='{:.2f}', numstring='{num}{multi}{unit}')
    def standardize(self, *args, **kwargs): return self.__class__(data=standardize_data(self.data), multiplier=Multiplier(), unit=Unit('σ'), numformat='{:.2f}', numstring='{num}{multi}{unit}')
    def minmax(self, *args, **kwargs): return self.__class__(data=minmax_data(self.data), multiplier=Multiplier('%'), unit=Unit(), numformat='{:.2f}', numstring='{num}{multi}{unit}')

    def group(self, *args, **kwargs): 
        attrs = {key:kwargs.get(key, value) for key, value in self.todict().items()}
        attrs['data'] = kwargs.get('data', group_data(self.data))
        return RangeSpec(**attrs)

   
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
        return self.headings[self.direction(value)] + self.delimiter.join([self.numstr(num) for num in value if num is not None])   
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
        attrs = {key:kwargs.get(key, value) for key, value in self.todict().items()}
        attrs['data'] = kwargs.get('data', average_data(weight, self.data))
        return NumSpec(**attrs)
    
    def cumulate(self, *args, direction, **kwargs):
        attrs = {key:kwargs.get(key, value) for key, value in self.todict().items()}
        attrs['data'] = kwargs.get('data', cumulate_data(direction, self.data))
        return NumSpec(**attrs)











