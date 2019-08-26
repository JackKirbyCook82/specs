# -*- coding: utf-8 -*-
"""
Created on Fri Apr 12 2018
@name:   TypeSpec Objects
@author: Jack Kirby Cook

"""

from specs.spec import Spec, SpecStringError, SpecValueError

__version__ = "1.0.0"
__author__ = "Jack Kirby Cook"
__all__ = ['CategorySpec']
__copyright__ = "Copyright 2018, Jack Kirby Cook"
__license__ = ""


_aslist = lambda items: [items] if not isinstance(items, (list, tuple, set)) else list(items)


def category_adapter(function):
    def wrapper(self, *args, databasis, **kwargs):
        assert isinstance(databasis, (tuple, list, set))
        function(self, *args, categories=set(databasis), **kwargs)
    return wrapper



@Spec.register('category')
class CategorySpec:
    delimiter = ' & '
    
    @property
    def categories(self): return self.__categories
    @category_adapter
    def __init__(self, *args, categories, **kwargs): 
        self.__categories = categories  
        super().__init__(*args, **kwargs)

    def checkstr(self, string): 
        if not bool(string): raise SpecStringError(self, string)
    def checkval(self, value):  
        if not all([item in self.__categories for item in value]): raise SpecValueError(self, _aslist(value))
    
    def asstr(self, value): return self.delimiter.join(value)
    def asval(self, string): return string.split(self.delimiter)

    def __eq__(self, other): return self.categories == other.categories        
    def todict(self): return dict(super().todict(), databasis=self.categories)
    
    # OPERATIONS
    def add(self, other, *args, **kwargs): return self.operation(other, *args, method='add', **kwargs)
    def subtract(self, other, *args, **kwargs): return self.operation(other, *args, method='subtract', **kwargs)
    







