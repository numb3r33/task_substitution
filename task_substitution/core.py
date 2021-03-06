# AUTOGENERATED! DO NOT EDIT! File to edit: 00_core.ipynb (unless otherwise specified).

__all__ = ['_pct_missing_values', '_preprocess_categorical', '_ignore_flds', '_split_train_test', '_split_by_null',
           '_shuffle']

# Cell
import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from .external_data import *

# Cell
def _pct_missing_values(feature:pd.Series)->float:
    """
    Given a feature calculates percentage of missing values
    """
    if not isinstance(feature, pd.Series): feature = pd.Series(feature)
    return feature.isnull().sum() / len(feature) * 100

# Cell
def _preprocess_categorical(cat_feat:pd.Series)->np.ndarray:
    """
    Given a categorical feature, label encode it.
    """
    return pd.Categorical(cat_feat).codes + 1

# Cell
def _ignore_flds(df:pd.DataFrame, ignore_flds:list)->pd.DataFrame:
    """
    Given a dataframe and list of fields to ignore, this method would drop them from the dataframe
    """
    df_cpy = df.copy()
    df_cpy.drop(ignore_flds, axis=1, inplace=True)
    return df_cpy

# Cell
def _split_by_null(df:pd.DataFrame, target_fld:str)->(pd.DataFrame, pd.DataFrame):
    """
    Given a dataframe with target name it would split df into two dataframes
    and shuffle both the dataframes as well, based on presence of value in the target feature or not.
    """
    mask = df[target_fld].notnull()
    train = df.loc[mask, :].sample(frac=1.)
    test  = df.loc[~mask, :].sample(frac=1.)

    return train, test

# Cell
def _split_train_test(df:pd.DataFrame, split_params:dict)->(pd.DataFrame,pd.DataFrame):
    """Splits a dataframe into train and test based on split parameters using sklearn.model_selection.train_test_split"""
    train, test = train_test_split(df, **split_params)
    return train, test

# Cell
def _shuffle(s:pd.Series)->(pd.Series):
    """Randomly reorders a series"""
    np.random.shuffle(s)
    return s