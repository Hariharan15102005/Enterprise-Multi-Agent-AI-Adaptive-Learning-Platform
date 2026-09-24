"""Preprocessing pipelines and feature transformers for OlistIQ ML models."""

import numpy as np
import pandas as pd
from typing import List, Optional
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder, RobustScaler
from sklearn.impute import SimpleImputer


class Log1pTransformer(BaseEstimator, TransformerMixin):
    """Applies log(1 + x) transformation to handle heavy right-skewed business distributions."""
    
    def __init__(self, columns: Optional[List[str]] = None):
        self.columns = columns
        
    def fit(self, X, y=None):
        return self
        
    def transform(self, X):
        X_copy = X.copy()
        if isinstance(X_copy, pd.DataFrame):
            cols = self.columns if self.columns else X_copy.columns
            for col in cols:
                if col in X_copy.columns:
                    X_copy[col] = np.log1p(np.maximum(0, X_copy[col].values))
            return X_copy
        return np.log1p(np.maximum(0, X))


def build_rfm_preprocessor(numerical_features: List[str]) -> Pipeline:
    """Builds preprocessing pipeline for customer RFM clustering."""
    return Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", RobustScaler()),
    ])


def build_tabular_preprocessor(
    numerical_features: List[str],
    categorical_features: List[str]
) -> ColumnTransformer:
    """Builds standard ColumnTransformer pipeline for supervised tabular classification/regression."""
    num_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
    ])
    
    cat_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="constant", fill_value="missing")),
        ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
    ])
    
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", num_pipeline, numerical_features),
            ("cat", cat_pipeline, categorical_features),
        ],
        remainder="drop"
    )
    return preprocessor
