# -*- coding: utf-8 -*-
"""
Created on Fri Apr 12 2018
@name:   TypeSpec Objects
@author: Jack Kirby Cook

"""

from specs.spec import Spec, SpecOperationNotSupportedError

__version__ = "1.0.0"
__author__ = "Jack Kirby Cook"
__all__ = ['CategorySpec', 'HistogramSpec']
__copyright__ = "Copyright 2018, Jack Kirby Cook"
__license__ = ""


ALL = '*'
DELIMITER = '|'

_aslist = lambda items: [items] if not isinstance(items, (list, tuple, set)) else list(items)


@Spec.register('category')
class CategorySpec:
    @property
    def categories(self): return self.__categories    
    def todict(self): return dict(**super().todict(), categories=list(set(self.categories)))    
    def __eq__(self, other): return set(self.categories) == set(other.categories)  
       
    def __init__(self, *args, categories, **kwargs): 
        assert isinstance(categories, (tuple, list, set))
        self.__categories = set(categories)  
        super().__init__(*args, **kwargs)

    def asstr(self, value): 
        assert all([item in self.__categories for item in _aslist(value)])
        return DELIMITER.join(_aslist(value))
        
    def asval(self, string): 
        assert isinstance(string, str)
        if string == ALL: return self.categories
        else: return string.split(DELIMITER)

    @classmethod
    def fromfile(cls, *args, databasis=[], **kwargs):
        assert isinstance(databasis, (tuple, list, set))
        assert len(set(databasis)) == len(databasis)
        return cls(*args, categories=set(databasis), **kwargs)

    # OPERATIONS
    def add(self, other, *args, **kwargs): 
        if other != self: raise SpecOperationNotSupportedError(self, other, 'add') 
        return self.operation(other, *args, method='add', **kwargs)
    
    def subtract(self, other, *args, **kwargs): 
        if other != self: raise SpecOperationNotSupportedError(self, other, 'subtract') 
        return self.operation(other, *args, method='subtract', **kwargs)
    
    def divide(self, other, *args, **kwargs): 
        if other != self: raise SpecOperationNotSupportedError(self, other, 'divide') 
        return self.operation(other, *args, method='divide', **kwargs)

    def couple(self, other, *args, **kwargs):
        if other != self: raise SpecOperationNotSupportedError(self, other, 'couple')  
        return self.operation(other, *args, method='couple', **kwargs)


@CategorySpec.register('histogram')
class HistogramSpec:
    def asstr(self, value): 
        assert all([key in self.__categories for key in value.keys()])
        return DELIMITER.join(['{key}={value}'.format(key=key, value=value) for key, value in self.items()])
                
    def asval(self, string):
        assert isinstance(string, str)
        items = {item.split('=')[0]:item.split[1] for item in string.split(DELIMITER)}
        return {category:items.get(category, 0) for category in self.__categories}

    # OPERATIONS
    def divide(self, other, *args, **kwargs): raise NotImplementedError('{}.{}()'.format(self.__class__.__name__, 'divide'))
    def couple(self, other, *args, **kwargs): raise NotImplementedError('{}.{}()'.format(self.__class__.__name__, 'couple'))












