# -*- coding: utf-8 -*-
"""
Created on Fri Apr 12 2018
@name:   SpecData Functions
@author: Jack Kirby Cook

"""

__version__ = "1.0.0"
__author__ = "Jack Kirby Cook"
__all__ = ['data_operation', 'data_transformation']
__copyright__ = "Copyright 2018, Jack Kirby Cook"
__license__ = ""


_FORMATTING = '/*+-_ |'


OPERATIONS = dict(multiply = '{data}*{other}', 
                  divide = '{data}/{other}')

TRANSFORMATIONS = {'factor': dict(multiply = '{factor}*{data}', 
                                  divide = '{factor}/{data}'),
                   'scale': dict(normalize = '{axis}|Quantiles|{data}', 
                                 standardize = '{axis}|ZScores|{data}', 
                                 minmax = '{axis}|MinMax|{data}'), 
                   'moving': dict(average = '{period}MAvg|{data}', 
                                  total = '{period}MTotal|{data}', 
                                  bracket = '{period}MRange|{data}', 
                                  differential='MDiff|{data}'),
                   'consolidate': dict(average = '{weight}Avg|{data}', 
                                       cumulate = '{direction}Cum|{data}',
                                       differential = 'Diff|{data}'), 
                   'unconsolidate': dict(cumulate = '{direction}UnCum|{data}', 
                                         group = 'Bins|{data}'),
                   'reduction': dict(summation = 'Sum{data}', 
                                     mean = 'Avg{data}', 
                                     stdev = 'StDev{data}', 
                                     minimum = 'Min{data}', 
                                     maximum = 'Max{data}',
                                     average = '{axis}|Avg{data}')}


def data_operation(data, other, *args, method, **kwargs):
    if method not in OPERATIONS.keys(): 
        assert data == other
        return data
    if any([opchar in data for opchar in _FORMATTING]): data = '({})'.format(data)  
    if any([opchar in data for opchar in _FORMATTING]): other = '({})'.format(other)      
    modifydata = OPERATIONS[method].format(data=data, other=other) if method in OPERATIONS else data
    return modifydata


def data_transformation(data, *args, method, how, **kwargs):
    if method not in TRANSFORMATIONS.keys():
        return data
    if any([opchar in data for opchar in _FORMATTING]): data = '({})'.format(data)
    modifydata = TRANSFORMATIONS[method][how].format(data=data, **kwargs)
    return modifydata














