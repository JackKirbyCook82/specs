# -*- coding: utf-8 -*-
"""
Created on Fri Apr 12 2018
@name:   Spec Object
@author: Jack Kirby Cook

"""

import os.path
from abc import ABC, abstractmethod
import json

from utilities.strings import uppercase

__version__ = "1.0.0"
__author__ = "Jack Kirby Cook"
__all__ = ['Spec', 'SpecStringError', 'SpecValueError', 'SpecOperationError', 'asstr', 'asval']
__copyright__ = "Copyright 2018, Jack Kirby Cook"
__license__ = ""


def asstr(function):
    def wrapper(self, value):
        self.checkval(value)
        string = function(self, value)
        self.checkstr(string)
        return string
    return wrapper

def asval(function):
    def wrapper(self, string):
        self.checkstr(string)
        value = function(self, string)
        self.checkval(value)
        return value
    return wrapper


def sametype(function):
    def wrapper(self, other, *args, **kwargs):
        if type(self) != type(other): raise TypeError(' != '.join([str(type(self)), str(type(other))]))
        if self.data != other.data: raise TypeError(' != '.join([self.name, other.name]))
        return function(self, other, *args, **kwargs)
    return wrapper


class SpecStringError(Exception): 
    def __init__(self, spec, string): super().__init__('{}({})'.format(spec.__class__.__name__, string))
class SpecValueError(Exception): 
    def __init__(self, spec, value): super().__init__('{}({})'.format(spec.__class__.__name__, value))
class SpecOperationError(Exception): 
    def __init__(self, spec, other, operation): super().__init__('{}.{}({})'.format(repr(spec), operation, repr(other)))
class SpecOperationNotSupportedError(Exception): 
    def __init__(self, spec, operation): super().__init__('{}.{}()'.format(repr(spec), operation))


class Spec(ABC):
    def __new__(cls, *args, **kwargs):
        if cls == Spec: return cls.subclasses()[kwargs['datatype']](*args, **kwargs)
        else:
            assert hasattr(cls, 'datatype')
            cls.asstr, cls.asval = asstr(cls.asstr), asval(cls.asval)
            cls.__eq__ = sametype(cls.__eq__)
            cls.add, cls.subtract = sametype(cls.add), sametype(cls.subtract)
            return super().__new__(cls)

    @property
    def data(self): return self.__data
    @property
    def name(self): return '_'.join([uppercase(self.data, index=0, withops=True), self.__class__.__name__])
    def __init__(self, *args, data, **kwargs): self.__data = data

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
    def __eq__(self, other): pass
    @abstractmethod
    def todict(self): pass

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
    def __ne__(self, other): return not self.__eq__(other)

    # OPERATIONS
    def __add__(self, other): return self.add(other)
    def __sub__(self, other): return self.subtract(other)
    def __mul__(self, other): return self.multiply(other)
    def __truediv__(self, other): return self.divide(other)
    
    def add(self, other, *args, **kwargs): 
        if self != other: raise SpecOperationError(self, other, 'add')
        return self
        
    def subtract(self, other, *args, **kwargs): 
        if self != other: raise SpecOperationError(self, other, 'subtract')
        return self
    
    def multiply(self, other, *args, **kwargs): raise SpecOperationNotSupportedError(self, 'multiply')
    def divide(self, other, *args, **kwargs): raise SpecOperationNotSupportedError(self, 'divide')
    
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
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    

    
    
    
    
    
    
    
    
    