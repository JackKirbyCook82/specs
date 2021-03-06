# -*- coding: utf-8 -*-
"""
Created on Fri Apr 12 2018
@name:   TypeSpec Objects
@author: Jack Kirby Cook

"""

from specs.spec import Spec, SpecOperationNotSupportedError, SpecTransformationNotSupportedError

__version__ = "1.0.0"
__author__ = "Jack Kirby Cook"
__all__ = ['CategorySpec', 'HistogramSpec']
__copyright__ = "Copyright 2018, Jack Kirby Cook"
__license__ = ""


ALL = '*'
DELIMITER = '|'
ASSIGNMENT = '@'

_aslist = lambda items: [items] if not isinstance(items, (list, tuple, set)) else list(items)


class CategorySpec(Spec, datatype='category'):
    @property
    def categories(self): return self.__categories
    @property
    def indexes(self): return self.__indexes
    
    def __hash__(self): return hash((self.data, self.datatype, self.categories, self.indexes,))
    def __eq__(self, other): 
        if type(self) != type(other): raise TypeError(type(other).__name__)
        if all([self.data != other.data, self.datatype != other.datatype]): raise TypeError(type(other).__name__)
        return self.categories == other.categories and self.indexes == other.indexes 
    
    def category(self, index): return self.categories[self.indexes.index(index)]
    def index(self, category): return self.indexes[self.categories.index(category)]
    def todict(self): return dict(**super().todict(), categories=self.categories, indexes=self.indexes)       
       
    def __init__(self, *args, categories, indexes, **kwargs): 
        assert isinstance(categories, (tuple, list)) and isinstance(indexes, (tuple, list))
        assert len(set(categories)) == len(categories) == len(set(indexes)) == len(indexes) 
        self.__categories = tuple(categories) 
        self.__indexes = tuple([int(index) for index in indexes])
        super().__init__(*args, **kwargs)

    def asval(self, string):
        assert isinstance(string, str)
        if string == ALL: return self.categories
        else: return tuple(string.split(DELIMITER))        

    def asstr(self, value): 
        assert all([item in self.__categories for item in _aslist(value)])
        return DELIMITER.join(_aslist(value))
        
    @classmethod
    def fromfile(cls, *args, databasis=[], **kwargs):
        assert isinstance(databasis, (tuple, list))
        categories, indexes = databasis[0::2], databasis[1::2]
        return cls(*args, categories=categories, indexes=indexes, **kwargs)

    # OPERATIONS
    def expand(self, *args, **kwargs):        
        return self.transformation(*args, method='expand', **kwargs)
    
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


class HistogramSpec(Spec, datatype='histogram'):
    @property
    def categories(self): return self.__categories
    @property
    def indexes(self): return self.__indexes

    def __hash__(self): return hash((self.data, self.datatype, self.categories, self.indexes,))
    def __eq__(self, other): 
        if type(self) != type(other): raise TypeError(type(other))
        if all([self.data != other.data, self.datatype != other.datatype]): raise TypeError(type(other))
        return self.categories == other.categories and self.indexes == other.indexes 
    
    def category(self, index): return self.categories[self.indexes.index(index)]
    def index(self, category): return self.indexes[self.categories.index(category)]
    def todict(self): return dict(**super().todict(), categories=self.categories, indexes=self.indexes)  
    
    def __init__(self, *args, categories, indexes, **kwargs): 
        assert isinstance(categories, (tuple, list)) and isinstance(indexes, (tuple, list))
        assert len(set(categories)) == len(categories) == len(set(indexes)) == len(indexes)   
        self.__categories = tuple(categories) 
        self.__indexes = tuple([int(index) for index in indexes])
        super().__init__(*args, **kwargs)
    
    def asval(self, string):
        assert isinstance(string, str)
        items = {item.split('=')[0]:item.split[1] for item in string.split(DELIMITER)}
        return {category:items.get(category, 0) for category in self.__categories}
    
    def asstr(self, value): 
        assert all([key in self.__categories for key in value.keys()])
        return DELIMITER.join([ASSIGNMENT.join([key, value]) for key, value in self.items()])

    @classmethod
    def fromfile(cls, *args, databasis=[], **kwargs):
        assert isinstance(databasis, (tuple, list))
        categories, indexes = databasis[0::2], databasis[1::2]
        return cls(*args, categories=categories, indexes=indexes, **kwargs)

    # OPERATIONS
    def add(self, other, *args, **kwargs): 
        if other != self: raise SpecOperationNotSupportedError(self, other, 'add') 
        return self.operation(other, *args, method='add', **kwargs)  
    
    def subtract(self, other, *args, **kwargs): 
        if other != self: raise SpecOperationNotSupportedError(self, other, 'subtract') 
        return self.operation(other, *args, method='subtract', **kwargs)






