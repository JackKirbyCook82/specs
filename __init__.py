# -*- coding: utf-8 -*-
"""
Created on Fri Jun 7 2019
@name:   Specs Module
@author: Jack Kirby Cook

"""

import os.path
import pandas as pd

import utilities.dataframes as dfs

from specs.spec import Spec
from specs.typespecs import CategorySpec, HistogramSpec
from specs.numspecs import NumSpec, RangeSpec

__version__ = "1.0.0"
__author__ = "Jack Kirby Cook"
__all__ = ['specs_fromfile', 'CategorySpec', 'HistogramSpec', 'NumSpec', 'RangeSpec']
__copyright__ = "Copyright 2018, Jack Kirby Cook"
__license__ = ""


_aslist = lambda items: [items] if not isinstance(items, (list, tuple)) else list(items)
_defaultparser = lambda item: str(item) if pd.notnull(item) else item
_allnull = lambda items: all([pd.isnull(item) for item in items])
_allnotnull = lambda items: all([pd.notnull(item) for item in items])


def specs_fromfile(specs_file, specs_parsers):
    if not os.path.isfile(specs_file): raise FileNotFoundError(specs_file)
    dataframe = dfs.dataframe_fromfile(specs_file)
    dataframe = dfs.dataframe_parser(dataframe, parsers=specs_parsers, defaultparser=_defaultparser)
    dataframe.set_index('datakey', drop=True, inplace=True)
    specdata = {key:{item:value for item, value in values.items() if not _allnull(_aslist(value))} for key, values in dataframe.transpose().to_dict().items() if not _allnull(_aslist(values))}
    return {key:Spec.fromfile(**values) for key, values in specdata.items()}
    












