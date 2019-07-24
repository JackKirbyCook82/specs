# -*- coding: utf-8 -*-
"""
Created on Fri Apr 12 2018
@name:   SpecData Functions
@author: Jack Kirby Cook

"""

from utilities.strings import uppercase

__version__ = "1.0.0"
__author__ = "Jack Kirby Cook"
__all__ = ['dataoperation', 'datatransformation']
__copyright__ = "Copyright 2018, Jack Kirby Cook"
__license__ = ""


OPERATIONS = {'multiply':'*', 'divide':'/'}
TRANSFORMATIONS = {'scale': dict(normalize='Quantiles', standardize='ZScores', minmax='MinMax'), 
                   'moving': dict(average='{period}MA', total='{period}MT', bracket='{period}MR'),
                   'consolidate': dict(average='{weight}Avg', cumulate='{direction}Cum'), 
                   'unconsolidate': dict(cumulate='{direction}UnCum'),
                   'reduction': dict(summation='Sum', mean='Mean', stdev='StDev', minimum='Min', maximum='Max', wtaverage='WtAvg')}


def dataoperation(data, other, *args, method, **kwargs):
    if method in OPERATIONS: return OPERATIONS[method].join([data, other])
    else: return data 


def datatransformation(data, *args, method, how, axis=None, **kwargs):
    axisstr = '[{axis}]'.format(axis=uppercase(axis)) if axis else ''
    modstr = TRANSFORMATIONS[method][how].format(**kwargs)
    datastr = '({data})'.format(data=data) if '_' in data else data
    return '_'.join([modstr, datastr])

