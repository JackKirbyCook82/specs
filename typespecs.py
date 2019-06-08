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


@Spec.register('category')
class CategorySpec:
    delimiter = ' & '
    
    @property
    def categories(self): return self.__categories
    def __init__(self, *args, databasis, **kwargs): 
        self.__categories = set(_aslist(databasis))    
        super().__init__(*args, **kwargs)
    
    def fixvalue(self, value): return set([item for item in _aslist(value) if item in self.__categories]) 
    
    def checkstr(self, string): 
        if not bool(string): raise SpecStringError(self, string)
    def checkval(self, value): 
        if not isinstance(value, set): raise SpecValueError(self, value)
        if not all([item in self.__categories for item in value]): raise SpecValueError(self, value)
    
    def asstr(self, value): return self.delimiter.join(value)
    def asval(self, string): return set(string.split(self.delimiter))

    def __eq__(self, other): return self.categories == other.categories
    def todict(self): return dict(data=self.data, datatype=self.datatype, databasis=self.categories)












