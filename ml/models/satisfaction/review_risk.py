"""Customer Satisfaction / Review Risk Prediction model.

Predicts whether an order is at risk of receiving a low review score (1-2 stars)
based on operational fulfillment metrics without using review text or post-review leakage.
"""

import logging
import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple, List
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline

from ml.features.definitions import (
    SATISFACTION_NUMERICAL_FEATURES,
    SATISFACTION_CATEGORICAL_FEATURES,
    SATISFACTION_FEATURES
)
from ml.preprocessing.transformers import build_tabular_preprocessor
from ml.evaluation.evaluator import evaluate_classification
from ml.config.ml_config import ml_config

logger = logging.getLogger("olistiq.ml.satisfaction")


class ReviewRiskClassifier:
    """Classifies risk of negative customer reviews from operational fulfillment signals."""

    def __init__(
        self,
        n_estimators: int = 100,
        random_state: int = ml_config.RANDOM_SEED
    ):
        self.n_estimators = n_estimators
        self.random_state = random_state
        self.numerical_features = SATISFACTION_NUMERICAL_FEATURES
        self.categorical_features = SATISFACTION_CATEGORICAL_FEATURES
        self.features = SATISFACTION_FEATURES
        
        self.preprocessor = build_tabular_preprocessor(
            self.numerical_features,
            self.categorical_features
        )
        
        self.estimator = RandomForestClassifier(
            n_estimators=self.n_estimators,
            max_depth=10,
            class_weight="balanced",
            random_state=self.random_state,
            n_jobs=-1
        )
        self.pipeline: Pipeline = None

    def fit(
        self,
        df_train: pd.DataFrame,
        df_test: pd.DataFrame
    ) -> Tuple["ReviewRiskClassifier", Dict[str, Any]]:
        """Trains satisfaction model and evaluates on test set."""
        X_train = df_train[self.features]
        y_train = df_train["is_negative_review"].values
        
        X_test = df_test[self.features]
        y_test = df_test["is_negative_review"].values
        
        self.pipeline = Pipeline([
            ("preprocessor", self.preprocessor),
            ("classifier", self.estimator)
        ])
        
        logger.info("Training ReviewRiskClassifier (RandomForest)...")
        self.pipeline.fit(X_train, y_train)
        
        y_pred = self.pipeline.predict(X_test)
        y_prob = self.pipeline.predict_proba(X_test)[:, 1]
        
        eval_metrics = evaluate_classification(y_test, y_pred, y_prob)
        logger.info(
            "Review Risk Test Metrics: ROC-AUC=%.4f, PR-AUC=%.4f, F1=%.4f, Recall=%.4f",
            eval_metrics["roc_auc"], eval_metrics["pr_auc"], eval_metrics["f1"], eval_metrics["recall"]
        )
        return self, eval_metrics

    def predict_risk(self, order_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Predicts probability of negative review and details underlying satisfaction drivers."""
        df_single = pd.DataFrame([order_dict])
        for col in self.features:
            if col not in df_single.columns:
                df_single[col] = 0.0 if col in self.numerical_features else "unknown"
                
        prob = float(self.pipeline.predict_proba(df_single[self.features])[0, 1])
        
        # Risk assessment
        is_high_risk = prob >= 0.50
        risk_level = "High" if prob >= 0.60 else ("Medium" if prob >= 0.35 else "Low")
        
        # Drivers of dissatisfaction
        drivers = []
        delay_days = order_dict.get("delivery_delay_vs_estimated_days", 0.0)
        if delay_days > 0:
            drivers.append({
                "factor": "Delivery SLA Breach",
                "detail": f"Order arrived {round(float(delay_days), 1)} days past estimated promise date.",
                "impact": "High"
            })
        if order_dict.get("total_delivery_duration_days", 0.0) > 20:
            drivers.append({
                "factor": "Extended Transit Duration",
                "detail": f"Total fulfillment transit time took {round(float(order_dict.get('total_delivery_duration_days', 0)), 1)} days.",
                "impact": "High"
            })
        if order_dict.get("seller_historical_review_score", 5.0) < 3.8:
            drivers.append({
                "factor": "Sub-par Seller Rating",
                "detail": f"Merchant average rating is {round(float(order_dict.get('seller_historical_review_score', 0)), 2)}/5.0.",
                "impact": "Medium"
            })
            
        return {
            "negative_review_risk": risk_level,
            "dissatisfaction_probability": round(prob, 4),
            "predicted_satisfaction_status": "At-Risk" if is_high_risk else "Likely Satisfied",
            "dissatisfaction_drivers": drivers
        }
