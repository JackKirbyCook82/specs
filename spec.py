# -*- coding: utf-8 -*-
"""
Created on Fri Apr 12 2018
@name:   Spec Object
@author: Jack Kirby Cook

"""

import os.path
from abc import ABC, abstractmethod
from functools import update_wrapper
import json

from utilities.strings import uppercase

from specs.data import DataManipulation

__version__ = "1.0.0"
__author__ = "Jack Kirby Cook"
__all__ = ['Spec', 'samespec', 'SpecStringError', 'SpecValueError', 'SpecOperationNotSupportedError', 'SpecTransformationNotSupportedError']
__copyright__ = "Copyright 2018, Jack Kirby Cook"
__license__ = ""


datatransformations = DataManipulation('{data}')
#datatransformations['normalize'] = '({axis}|quantiles_{data})'
#datatransformations['standardize'] = '({axis}|zscores_{data})'
#datatransformations['minmax'] = '({axis}|minmax_{data})'

#datatransformations['mean'] = '({axis}|mean_{data})'
#datatransformations['summuation'] = '({axis}|sum_{data})'
#datatransformations['stdev'] = '({axis}|stdev_{data})'
#datatransformations['minimum'] = '({axis}|min_{data})'
#datatransformations['maximum'] = '({axis}|max_{data})'

#datatransformations['weightaverage'] = '({axis}|wtavg_{data})'

#datatransformations['movingaverage'] = '({axis}|{period}mavg_{data})'
#datatransformations['movingtotal'] = '({axis}|{period}mtot_{data})'
#datatransformations['movingbracket'] = '({axis}|{period}mrange_{data})'

#datatransformations['uncumulate'] = '({direction}|uncum_{data})'
#datatransformations['average'] = '({weight}|avg_{data})'
#datatransformations['cumulate'] = '({direction}|cum_{data})'

#datatransformations['bounded'] = '(bounded_{data})'

dataoperations = DataManipulation('{data}')
dataoperations['multiply'] = '({data}*{other})'
dataoperations['divide'] = '({data}/{other})'


def samespec(function):
    def wrapper(self, other, *args, **kwargs):
        if type(self) != type(other): raise SpecOperationNotSupportedError(self, other, function.__name__)
        if self.data != other.data: raise SpecOperationNotSupportedError(self, other, function.__name__)
        return function(self, other, *args, **kwargs)    
    update_wrapper(wrapper, function)
    return wrapper


class SpecStringError(Exception): 
    def __init__(self, spec, string): super().__init__('{}({})'.format(spec.__class__.__name__, string))
class SpecValueError(Exception): 
    def __init__(self, spec, value): super().__init__('{}({})'.format(spec.__class__.__name__, value))

class SpecOperationNotSupportedError(Exception): 
    def __init__(self, spec, other, operation): super().__init__('{}.{}({})'.format(repr(spec), operation, repr(other)))
class SpecTransformationNotSupportedError(Exception):
    def __init__(self, spec, transformation, method): super().__init__('{}.{}(method={})'.format(repr(spec), transformation, method))   
       
    
class Spec(ABC):
    def __new__(cls, *args, **kwargs):
        if cls == Spec: return cls.subclasses()[kwargs['datatype']](*args, **kwargs)
        else:
            assert hasattr(cls, 'datatype')
            return super().__new__(cls)

    @property
    def data(self): return self.__data
    @property
    def name(self): return '_'.join([uppercase(self.data, index=0, withops=True), self.__class__.__name__, 'Spec'])
    @property
    def jsonstr(self): return json.dumps(self.todict(), sort_keys=True, indent=3, separators=(',', ' : '))  
    def __init__(self, *args, data, **kwargs): self.__data = data
    
    def __add__(self, other): return self.add(other)
    def __sub__(self, other): return self.subtract(other)
    def __mul__(self, other): return self.multiply(other)
    def __truediv__(self, other): return self.divide(other)    
    
    # ABSTRACT INSTANCE METHODS    
    @abstractmethod
    def asstr(value): pass
    @abstractmethod
    def asval(string): pass
    @abstractmethod
    def checkstr(string): pass
    @abstractmethod
    def checkval(value): pass
    @abstractmethod
    def todict(self): pass
    @abstractmethod
    def __eq__(self, other): pass

    # REGISTER SUBCLASSES  
    __subclasses = {}      
    @classmethod
    def subclasses(cls): return cls.__subclasses     
    
    @classmethod
    def register(cls, datatype):  
        def wrapper(subclass):
            name = subclass.__name__
            bases = (subclass, cls)
            newsubclass = type(name, bases, dict(datatype=datatype))
            Spec.__subclasses[datatype] = newsubclass
            return newsubclass
        return wrapper  

    # EQUALITY
    @samespec
    def __ne__(self, other): return not self.__eq__(other)

    # OPERATIONS
    def operation(self, other, *args, method, **kwargs):
        datatype = kwargs.get('datatype', self.datatype)
        attrs = {key:kwargs.get(key, value) for key, value in self.todict().items()}
        attrs['data'] = dataoperations[method](data=self.data, other=other.data, method=method, **kwargs)
        return self.subclasses()[datatype](**attrs)        
    
    # TRANSFORMATIONS
    def transformation(self, *args, method, how, **kwargs):
        datatype = kwargs.get('datatype', self.datatype)
        attrs = {key:kwargs.get(key, value) for key, value in self.todict().items()}
        attrs['data'] = datatransformations[method](data=self.data, method=method, how=how, **kwargs)
        return self.subclasses()[datatype](**attrs)
        
    # FILES
    def tojson(self, file):
        with open(file, 'w') as outfile:          
            json.dump(self.todict(), outfile, sort_keys=True, indent=3, separators=(',', ' : '))    
    
    @classmethod
    def fromjson(cls, file):
        if not os.path.isfile(file): raise FileNotFoundError(file)
        with open(file, 'r') as infile:          
            attrs = json.load(infile)
        return cls(**attrs)   
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    

    
    
    
    
    
    
    
    
    