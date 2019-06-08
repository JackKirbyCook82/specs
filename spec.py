# -*- coding: utf-8 -*-
"""
Created on Fri Apr 12 2018
@name:   Spec Object
@author: Jack Kirby Cook

"""

import os.path
from abc import ABC, abstractmethod
import json

__version__ = "1.0.0"
__author__ = "Jack Kirby Cook"
__all__ = ['Spec', 'SpecStringError', 'SpecValueError', 'asstr', 'asval']
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
    def wrapper(self, other):
        if type(self) != type(other): raise TypeError(' != '.join([str(type(self)), str(type(other))]))
        return function(self, other)
    return wrapper


class SpecStringError(Exception): 
    def __init__(self, spec, string): super().__init__('{}({})'.format(spec.__class__.__name__, string))
class SpecValueError(Exception): 
    def __init__(self, spec, value): super().__init__('{}({})'.format(spec.__class__.__name__, value))


class Spec(ABC):
    def __new__(cls, *args, **kwargs):
        if cls == Spec: return cls.subclasses()[kwargs['datatype']](*args, **kwargs)
        else:
            assert hasattr(cls, 'datatype')
            cls.asstr, cls.asval = asstr(cls.asstr), asval(cls.asval)
            cls.__eq__ = sametype(cls.__eq__)
            return super().__new__(cls)

    @property
    def data(self): return self.__data
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
    
    # FILES
    def tojson(self, file):
        with open(file, 'w') as outfile:          
            json.dump(self.todict(), outfile, sort_keys=True, indent=3, separators=(',', ' : '))    
    
    @classmethod
    def fromjson(cls, file):
        if not os.path.isfile(file): raise FileNotFoundError(file)
        with open(file, 'r') as infile:          
            json_dict = json.load(infile)
        return cls(**json_dict)   
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    

    
    
    
    
    
    
    
    
    