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
    def __init__(self, target_fld:str, cat_flds:list=None, ignore_flds:list=None, perf_fn=None, split_args:dict=None, model_args:dict=None):
        self.dataset_args = {'target_fld': target_fld,
                             'cat_flds': cat_flds,
                             'ignore_flds': ignore_flds
                            }

        self.perf_fn = perf_fn
        self.split_args = split_args
        self.model_args = model_args

    def cv(self, X_train, y_train, X_test):
        model = Model(**self.model_args)
        fold_runs = model.cv(X_train, y_train, self.perf_fn)

        return fold_runs

    def recover(self, X_train, y_train, X_test):
        model = Model(**self.model_args)
        self.trained_model = model.fit(X_train, y_train)
        recovered_values = self.trained_model.predict(X_test)

        return recovered_values

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
        train, test = Dataset.split_train_test_by_null(df_cpy, self.dataset_args['target_fld'])


        # further split train into tr and te
        # do cross-validation on tr and report final performance
        # on te
        tr, te = Dataset.split_train_test(train, self.split_args)

        ytr = tr[self.dataset_args['target_fld']]
        xtr = tr.drop(self.dataset_args['target_fld'], axis=1)
        yte = te[self.dataset_args['target_fld']]
        xte = te.drop(self.dataset_args['target_fld'], axis=1)

        fold_runs = self.cv(xtr, ytr, xte)
        pred = self.recover(xtr, ytr, xte)
        unseen_perf = self.perf_fn(yte, pred)
        print(f'Performance on unseen dataset: {unseen_perf:.3f}')


        # create target variable
        y_train = train[self.dataset_args['target_fld']]
        X_train = train.drop(self.dataset_args['target_fld'], axis=1)

        X_test = test.drop(self.dataset_args['target_fld'], axis=1)

        # train model to recover missing values
        y_test = self.recover(X_train, y_train, X_test)
        y_test = pd.Series(y_test, index=test.index)

        recovered_target = pd.concat([y_train, y_test]).reindex(orig_index_order)
        df_cpy.loc[:, self.dataset_args['target_fld']] = recovered_target

        return df_cpy