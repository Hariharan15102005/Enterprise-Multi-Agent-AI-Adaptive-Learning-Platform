"""Delivery Delay Risk Prediction model.

Predicts the likelihood that an order will be delivered past its estimated delivery date.
Enforces strict prevention of post-purchase data leakage.
"""

import logging
import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple, List, Optional
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.pipeline import Pipeline

from ml.features.definitions import (
    DELIVERY_RISK_NUMERICAL_FEATURES,
    DELIVERY_RISK_CATEGORICAL_FEATURES,
    DELIVERY_RISK_FEATURES
)
from ml.preprocessing.transformers import build_tabular_preprocessor
from ml.evaluation.evaluator import evaluate_classification
from ml.config.ml_config import ml_config

logger = logging.getLogger("olistiq.ml.delivery_risk")


class DeliveryRiskClassifier:
    """Classifies order delay risk using pre-fulfillment logistics and seller attributes."""

    def __init__(
        self,
        model_type: str = "HistGradientBoosting",
        random_state: int = ml_config.RANDOM_SEED
    ):
        self.model_type = model_type
        self.random_state = random_state
        self.numerical_features = DELIVERY_RISK_NUMERICAL_FEATURES
        self.categorical_features = DELIVERY_RISK_CATEGORICAL_FEATURES
        self.features = DELIVERY_RISK_FEATURES
        
        self.preprocessor = build_tabular_preprocessor(
            self.numerical_features,
            self.categorical_features
        )
        
        if self.model_type == "RandomForest":
            self.estimator = RandomForestClassifier(
                n_estimators=100,
                max_depth=12,
                class_weight="balanced",
                random_state=self.random_state,
                n_jobs=-1
            )
        else:
            self.estimator = HistGradientBoostingClassifier(
                max_iter=ml_config.DELIVERY_MAX_ITER,
                learning_rate=ml_config.DELIVERY_LEARNING_RATE,
                min_samples_leaf=ml_config.DELIVERY_MIN_SAMPLES_LEAF,
                class_weight="balanced",
                random_state=self.random_state
            )
            
        self.pipeline: Pipeline = None

    def fit(
        self,
        df_train: pd.DataFrame,
        df_test: pd.DataFrame
    ) -> Tuple["DeliveryRiskClassifier", Dict[str, Any]]:
        """Trains classifier and evaluates out-of-time test set."""
        X_train = df_train[self.features]
        y_train = df_train["is_delivered_late"].values
        
        X_test = df_test[self.features]
        y_test = df_test["is_delivered_late"].values
        
        self.pipeline = Pipeline([
            ("preprocessor", self.preprocessor),
            ("classifier", self.estimator)
        ])
        
        logger.info("Training DeliveryRiskClassifier (%s)...", self.model_type)
        self.pipeline.fit(X_train, y_train)
        
        y_pred = self.pipeline.predict(X_test)
        y_prob = self.pipeline.predict_proba(X_test)[:, 1]
        
        eval_metrics = evaluate_classification(y_test, y_pred, y_prob)
        logger.info(
            "Delivery Risk Test Metrics: ROC-AUC=%.4f, PR-AUC=%.4f, F1=%.4f, Recall=%.4f",
            eval_metrics["roc_auc"], eval_metrics["pr_auc"], eval_metrics["f1"], eval_metrics["recall"]
        )
        return self, eval_metrics

    def predict_risk(self, order_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Infers delay risk probability, tier, and actionable risk factors."""
        df_single = pd.DataFrame([order_dict])
        for col in self.features:
            if col not in df_single.columns:
                df_single[col] = 0.0 if col in self.numerical_features else "unknown"
                
        prob = float(self.pipeline.predict_proba(df_single[self.features])[0, 1])
        
        # Risk Tiers
        if prob >= 0.65:
            risk_level = "High"
        elif prob >= 0.35:
            risk_level = "Medium"
        else:
            risk_level = "Low"
            
        # Interpret risk factors
        risk_factors = []
        if order_dict.get("haversine_distance_km", 0) > 1000:
            risk_factors.append({
                "factor": "Long Distance Transit",
                "detail": f"Inter-regional shipment spanning {round(float(order_dict.get('haversine_distance_km', 0)))} km.",
                "severity": "High"
            })
        if order_dict.get("seller_historical_delay_rate", 0) > 10.0:
            risk_factors.append({
                "factor": "Seller SLA History",
                "detail": f"Seller has a {round(float(order_dict.get('seller_historical_delay_rate', 0)), 1)}% historical breach rate.",
                "severity": "High"
            })
        if order_dict.get("is_interstate_shipment", 0) == 1:
            risk_factors.append({
                "factor": "Interstate Cross-Border Logistics",
                "detail": f"Crosses state lines from {order_dict.get('seller_state', 'Unknown')} to {order_dict.get('customer_state', 'Unknown')}.",
                "severity": "Medium"
            })
        if order_dict.get("freight_ratio_pct", 0) > 30.0:
            risk_factors.append({
                "factor": "High Freight Weight/Volume Burden",
                "detail": f"Freight comprises {round(float(order_dict.get('freight_ratio_pct', 0)), 1)}% of total value.",
                "severity": "Low"
            })
            
        if not risk_factors:
            risk_factors.append({
                "factor": "Standard Local Delivery",
                "detail": "Normal distance and reliable seller profile.",
                "severity": "None"
            })
            
        return {
            "risk_level": risk_level,
            "delay_probability": round(prob, 4),
            "estimated_delivery_duration_days": order_dict.get("estimated_delivery_duration_days"),
            "risk_factors": risk_factors,
            "model_type": self.model_type
        }
