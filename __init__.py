# -*- coding: utf-8 -*-
"""
Created on Fri Jun 7 2019
@name:   Spec Objects
@author: Jack Kirby Cook

"""

import sys
import os.path
import inspect
import pandas as pd

import utilities.dataframes as dfs

from specs.spec import Spec
from specs.typespecs import *
from specs.numspecs import *


def import_specs():
    subclasses = []
    for name, obj in inspect.getmembers(sys.modules[__name__]):
        if inspect.isclass(obj): 
            if issubclass(obj, Spec): subclasses.append(obj)
    return subclasses


__version__ = "1.0.0"
__author__ = "Jack Kirby Cook"
__all__ = [str(cls.__name__) for cls in import_specs()]
__copyright__ = "Copyright 2018, Jack Kirby Cook"
__license__ = ""


_INDEXKEY = 'key'
_aslist = lambda items: [items] if not isinstance(items, (list, tuple)) else list(items)
_allnull = lambda items: all([pd.isnull(item) for item in items])

def parser(item, splitby): 
    if _allnull(_aslist(item)): return ''
    else: return item.split(splitby) if splitby in item else str(item)
    
def antiparser(item, concatby): 
    if _allnull(_aslist(item)): return ''
    else: return concatby.join([str(i) for i in item]) if isinstance(item, (set, tuple, list)) else str(item)


def specs_fromfile(file, parserchar=';'):
    if not os.path.isfile(file): raise FileNotFoundError(file)
    dataframe = dfs.dataframe_fromfile(file)
    dataframe = dfs.dataframe_parser(dataframe, default=lambda item: parser(item, parserchar))
    dataframe.set_index(_INDEXKEY, drop=True, inplace=True)
    specdata = {key:{item:value for item, value in values.items() if not _allnull(_aslist(value))} for key, values in dataframe.transpose().to_dict().items() if not _allnull(_aslist(values))}
    return {key:Spec(**values) for key, values in specdata.items()}
    

def specs_tofile(file, specs, antiparserchar=';'):
    assert isinstance(specs, dict)
    dataframe = pd.DataFrame({key:value.todict() for key, value in specs.items()}).transpose()
    dataframe.index.name = _INDEXKEY
    dataframe = dfs.dataframe_parser(dataframe, default=lambda item: antiparser(item, antiparserchar))
    dataframe.reset_index(drop=False, inplace=True)
    dfs.dataframe_tofile(file, dataframe, index=False, header=True)
















