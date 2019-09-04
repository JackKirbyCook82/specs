# -*- coding: utf-8 -*-
"""
Created on Fri Apr 12 2018
@name:   SpecData Functions
@author: Jack Kirby Cook

"""

__version__ = "1.0.0"
__author__ = "Jack Kirby Cook"
__all__ = ['dataoperation', 'datatransformation']
__copyright__ = "Copyright 2018, Jack Kirby Cook"
__license__ = ""


OPERATION_CHARS = '/*+-_ |'

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
                                     mean = 'Mean{data}', 
                                     stdev = 'StDev{data}', 
                                     minimum = 'Min{data}', 
                                     maximum = 'Max{data}',
                                     wtaverage = 'WtAvg{data}')}


def dataoperation(data, other, *args, method, **kwargs):
    if any([opchar in data for opchar in OPERATION_CHARS]): data = '({})'.format(data)  
    if any([opchar in data for opchar in OPERATION_CHARS]): other = '({})'.format(other)      
    modifydata = OPERATIONS[method].format(data=data, other=other) if method in OPERATIONS else data
    return modifydata


def datatransformation(data, *args, method, how, **kwargs):
    if any([opchar in data for opchar in OPERATION_CHARS]): data = '({})'.format(data)
    modifydata = TRANSFORMATIONS[method][how].format(data=data, **kwargs)
    return modifydata














