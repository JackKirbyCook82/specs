# -*- coding: utf-8 -*-
"""
Created on Fri Apr 12 2018
@name:   Data Manipulation Object
@author: Jack Kirby Cook

"""

__version__ = "1.0.0"
__author__ = "Jack Kirby Cook"
__all__ = ['DataManipulation']
__copyright__ = "Copyright 2018, Jack Kirby Cook"
__license__ = ""


parse_strformat = lambda strformat: [item.split('}')[0] for item in strformat.split('{') if '}' in item]


class DataManipulation(dict):
    def __init__(self, dataformat): super().__init__({'default':self.decorator(dataformat)})
    def __setitem__(self, data, dataformat): super().__setitem__(data, self.decorator(dataformat)) 
    def __getitem__(self, data): return super().__getitem__(data if data in self.keys() else 'default')
    
    def decorator(self, dataformat):
        assert isinstance(dataformat, str)        
        keys = parse_strformat(dataformat)
                
        def wrapper(**kwargs): 
            assert all([key in kwargs.keys() for key in keys])
            return dataformat.format(**kwargs)                         
        return wrapper
    
    
