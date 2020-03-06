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


FORMATTING = '/*+-_ |'
OPERATIONS = {
    'multiply':'{data}*{other}', 
    'divide':'{data}/{other}'}
TRANSFORMATIONS = {
    'factor': {
        'multiply':'{factor}*{data}', 
        'divide':'{factor}/{data}'},
    'scale': {
        'normalize':'{axis}|quantiles|{data}', 
        'standardize':'{axis}|zscores|{data}', 
        'minmax':'{axis}|minmax|{data}'}, 
    'moving': {
        'average':'{period}mavg|{data}', 
        'summation':'{period}msum|{data}',
        'couple':'{period}mgrp|{data}'},
    'consolidate': {
        'average':'{weight}avg|{data}', 
        'cumulate':'{direction}cum|{data}',
        'differential':'diff|{data}'}, 
    'unconsolidate': {
        'cumulate':'{direction}uncum|{data}', 
        'couple':'coupled|{data}'},
    'reduction': {
        'average':'avg|{data}', 
        'stdev':'stdev|{data}', 
        'minimum':'min|{data}', 
        'maximum':'max|{data}'},
    'wtreduction': {
        'average':'{axis}|wtavg|{data}',
        'stdev':'{axis}|wtstdev|{data}',
        'median':'{axis}|wtmid|{data}'}}


def data_operation(data, other, *args, method, **kwargs):
    if method not in OPERATIONS.keys(): 
        assert data == other
        return data
    if any([opchar in data for opchar in FORMATTING]): data = '({})'.format(data)  
    if any([opchar in data for opchar in FORMATTING]): other = '({})'.format(other)      
    modifydata = OPERATIONS[method].format(data=data, other=other) if method in OPERATIONS else data
    return modifydata


def data_transformation(data, *args, method, how, axis=None, **kwargs):
    if method not in TRANSFORMATIONS.keys(): return data
    if how not in TRANSFORMATIONS[method].keys(): return data
    if any([opchar in data for opchar in FORMATTING]): data = '({})'.format(data)
    modifydata = TRANSFORMATIONS[method][how].format(data=data, axis=axis if axis else '', **kwargs)
    if modifydata[0] in FORMATTING: modifydata = modifydata[1:]
    return modifydata














