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


OPERATIONS = {'multiply':'{data}*{other}', 
              'divide'  :'{data}/{other}'}
TRANSFORMATIONS = {'factor'       :{'multiply'    :'{factor}*{data}', 
                                    'divide'      :'{factor}/{data}'},
                   'scale'        :{'normalize'   :'{axis}|Quantiles|{data}', 
                                    'standardize' :'{axis}|ZScores|{data}', 
                                    'minmax'      :'{axis}|MinMax|{data}'}, 
                   'moving'       :{'average'     :'{period}MAvg|{data}', 
                                    'summation'   :'{period}MSum|{data}',
                                    'couple'      :'{period}MGrp|{data}'},
                   'consolidate'  :{'average'     :'{weight}Avg|{data}', 
                                    'cumulate'    :'{direction}Cum|{data}',
                                    'differential':'Diff|{data}'}, 
                   'unconsolidate':{'cumulate'    :'{direction}UnCum|{data}', 
                                    'couple'      :'Coupled|{data}'},
                   'reduction'    :{'average'     :'Avg|{data}', 
                                    'stdev'       :'Stdev|{data}', 
                                    'minimum'     :'Min|{data}', 
                                    'maximum'     :'Max|{data}'},
                   'wtreduction'  :{'average'     :'{axis}|WtAvg|{data}',
                                    'stdev'       :'{axis}|WtStdev|{data}',
                                    'median'      :'{axis}|WtMed|{data}'}}


def data_operation(data, other, *args, method, **kwargs):
    if method not in OPERATIONS.keys(): 
        assert data == other
        return data
    if any([opchar in data for opchar in _FORMATTING]): data = '({})'.format(data)  
    if any([opchar in data for opchar in _FORMATTING]): other = '({})'.format(other)      
    modifydata = OPERATIONS[method].format(data=data, other=other) if method in OPERATIONS else data
    return modifydata


def data_transformation(data, *args, method, how, **kwargs):
    if method not in TRANSFORMATIONS.keys(): return data
    if how not in TRANSFORMATIONS[method].keys(): return data
    if any([opchar in data for opchar in _FORMATTING]): data = '({})'.format(data)
    modifydata = TRANSFORMATIONS[method][how].format(data=data, **kwargs)
    return modifydata














