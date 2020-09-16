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

from specs.specdata import data_operation, data_transformation

__version__ = "1.0.0"
__author__ = "Jack Kirby Cook"
__all__ = ['Spec', 'SpecOperationNotSupportedError', 'SpecTransformationNotSupportedError']
__copyright__ = "Copyright 2018, Jack Kirby Cook"
__license__ = ""


class SpecOperationNotSupportedError(Exception): 
    def __init__(self, spec, other, operation): super().__init__('{}.{}({})'.format(repr(spec), operation, repr(other)))
class SpecTransformationNotSupportedError(Exception):
    def __init__(self, spec, transformation, method): super().__init__('{}.{}(method={})'.format(repr(spec), transformation, method))   
    
    
class Spec(ABC):
    __registry = {}
    @classmethod
    def registry(cls): return cls.__registry
    def __init_subclass__(cls, datatype, *args, **kwargs):
        super().__init_subclass__(**kwargs)
        setattr(cls, 'datatype', datatype.lower())

    def __init__(self, *args, data, **kwargs): self.__data = data
    def __new__(cls, *args, **kwargs):
        if cls == Spec: return cls.__registry[kwargs['datatype'].lower()](*args, **kwargs)
        else: return super().__new__(cls)

    @property
    def data(self): return self.__data
    @property
    def dataname(self): return uppercase(self.__data, withops=True)
    @property
    def name(self): return '_'.join([self.dataname, uppercase(self.datatype, withops=True), 'Spec'])        
    
    def jsonstr(self): return json.dumps(self.todict(), sort_keys=True, indent=3, separators=(',', ' : '), default=str)  
    def todict(self): return dict(data=self.data, datatype=self.datatype)    
    
    def __add__(self, other): return self.add(other)
    def __sub__(self, other): return self.subtract(other)
    def __mul__(self, other): return self.multiply(other)
    def __truediv__(self, other): return self.divide(other)    
    def __str__(self): return self.jsonstr()
    def __ne__(self, other): return not self.__eq__(other)
    
    # ABSTRACT INSTANCE METHODS    
    @abstractmethod
    def asval(string): pass
    @abstractmethod
    def asstr(value): pass
    @abstractmethod
    def __eq__(self, other): pass
    @abstractmethod
    def __hash__(self): pass 

    # OPERATIONS
    def operation(self, other, *args, method, **kwargs):
        datatype = kwargs.get('datatype', self.datatype)
        attrs = {key:kwargs.get(key, value) for key, value in self.todict().items()}
        attrs['data'] = data_operation(self.data, other.data, *args, method=method, **kwargs)
        return self.registry[datatype](**attrs)        
    
    # TRANSFORMATIONS
    def transformation(self, *args, method, how, **kwargs):
        datatype = kwargs.get('datatype', self.datatype)
        attrs = {key:kwargs.get(key, value) for key, value in self.todict().items()}
        attrs['data'] = data_transformation(self.data, *args, method=method, how=how, **kwargs)
        return self.registry[datatype](**attrs)   
        
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
    
    @classmethod
    def fromfile(cls, *args, data, datatype, databasis, **kwargs):
        return cls.registry()[datatype].fromfile(*args, data=data, datatype=datatype, databasis=databasis, **kwargs)
   
    
    
    
    
    
    
    
    
    
    
    
    
    
    

    
    
    
    
    
    
    
    
    