# AUTOGENERATED! DO NOT EDIT! File to edit: 03_recover_missing.ipynb (unless otherwise specified).

__all__ = ['RecoverMissing']

# Cell
import pandas as pd
import numpy as np

from .data import *
from .model import *
from .external_data import *

# Cell
class RecoverMissing:
    """Recover missing values for a feature using task substitution."""
    def __init__(self, missing_fld:str, cat_flds:list=None, ignore_flds:list=None, **model_args):
        self.dataset_args = {'missing_fld': missing_fld,
                             'cat_flds': cat_flds,
                             'ignore_flds': ignore_flds
                            }
        self.model_args = model_args

    def recover(self, X_train, y_train, X_test):

        perf_fn = self.model_args['perf_fn']
        del self.model_args['perf_fn']

        model = Model(**self.model_args)
        fold_runs = model.cv(X_train, y_train, perf_fn)

        self.trained_model = model.fit(X_train, y_train)
        self.recovered_values = self.trained_model.predict(X_test)

        return fold_runs, self.recovered_values

    def run(self, df):
        df_cpy = df.copy()

        # create dataset class
        data = Dataset(df_cpy, **self.dataset_args)

        # label encode categorical variables
        df_cpy = data.preprocess()

        # store original index so that we can reindex the dataframe later
        # to preserve the index of the original dataframe.
        orig_index_order = df_cpy.index

        # split the dataset into train and test based on missing values in the
        # feature which we want to recover
        train, test = Dataset.split_train_test(df_cpy, self.dataset_args['missing_fld'])

        # create target variable
        y_train = train[self.dataset_args['missing_fld']]
        X_train = train.drop(self.dataset_args['missing_fld'], axis=1)

        X_test = test.drop(self.dataset_args['missing_fld'], axis=1)

        # train model to recover missing values
        fold_runs, y_test = self.recover(X_train, y_train, X_test)
        self.fold_runs = fold_runs

        y_test = pd.Series(y_test, index=test.index)

        recovered_target = pd.concat([y_train, y_test]).reindex(orig_index_order)
        df_cpy.loc[:, self.dataset_args['missing_fld']] = recovered_target

        return df_cpy