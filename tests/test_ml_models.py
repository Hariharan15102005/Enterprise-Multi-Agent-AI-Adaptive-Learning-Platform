"""Unit tests for ML models, feature definitions, registry, and data leakage prevention."""

import pytest
import numpy as np
import pandas as pd
from ml.features.definitions import (
    RFM_FEATURES,
    DELIVERY_RISK_FEATURES,
    SATISFACTION_FEATURES,
    DELIVERY_RISK_NUMERICAL_FEATURES,
)
from ml.models.customer_segmentation.rfm_clustering import CustomerSegmentationModel
from ml.models.delivery_risk.delay_classifier import DeliveryRiskClassifier
from ml.models.satisfaction.review_risk import ReviewRiskClassifier
from ml.models.forecasting.demand_forecaster import DemandForecaster
from ml.models.anomaly_detection.business_anomalies import BusinessAnomalyDetector
from ml.registry.model_registry import ModelRegistry


def test_data_leakage_strict_prevention():
    """Verify that post-fulfillment timestamps and leakage columns are strictly absent from features."""
    forbidden_leakage_columns = [
        "delivered_customer_timestamp",
        "delivered_carrier_timestamp",
        "order_delivered_customer_date",
        "order_delivered_carrier_date",
        "carrier_transit_days",
        "actual_delivery_duration_days",
        "total_delivery_days",
        "delivery_delay_days",
        "review_score",
        "review_comment_message",
        "review_comment_title",
        "sentiment_score",
        "sentiment_label"
    ]
    for col in forbidden_leakage_columns:
        assert col not in DELIVERY_RISK_FEATURES, f"Data leakage violation: '{col}' found in DELIVERY_RISK_FEATURES!"

    # Satisfaction model must not use review text or review scores as input features
    assert "review_score" not in SATISFACTION_FEATURES
    assert "review_comment_message" not in SATISFACTION_FEATURES
    assert "review_comment_title" not in SATISFACTION_FEATURES


def test_customer_segmentation_pipeline():
    """Verify customer RFM clustering pipeline, profile creation, and explanation."""
    np.random.seed(42)
    synthetic_data = pd.DataFrame({
        "recency_days": np.random.uniform(5, 400, 100),
        "frequency_orders": np.random.choice([1, 2, 3], size=100, p=[0.8, 0.15, 0.05]),
        "monetary_spend_brl": np.random.exponential(150, 100),
        "avg_order_value": np.random.exponential(120, 100),
        "avg_items_per_order": np.random.uniform(1.0, 2.5, 100),
        "category_diversity": np.random.choice([1, 2], 100),
        "customer_state": ["SP"] * 100
    })

    model = CustomerSegmentationModel(n_clusters=3, random_state=42)
    fitted_model, eval_metrics = model.fit(synthetic_data)

    assert "silhouette_score" in eval_metrics
    assert eval_metrics["n_clusters"] == 3
    assert len(fitted_model.cluster_profiles) == 3

    # Prediction test
    preds = fitted_model.predict(synthetic_data.head(5))
    assert "cluster_id" in preds.columns
    assert "segment_name" in preds.columns

    # Explanation test
    explanation = fitted_model.explain_customer(synthetic_data.iloc[0].to_dict())
    assert "cluster_id" in explanation
    assert "segment_name" in explanation
    assert "benchmark_comparison" in explanation


def test_delivery_risk_classifier():
    """Verify delivery delay classification inference and probability calibration."""
    np.random.seed(42)
    n = 200
    train_df = pd.DataFrame({
        "total_items_price_brl": np.random.uniform(20, 500, n),
        "total_freight_value_brl": np.random.uniform(10, 80, n),
        "freight_ratio_pct": np.random.uniform(5, 40, n),
        "total_item_count": np.random.choice([1, 2, 3], n),
        "unique_product_count": np.random.choice([1, 2], n),
        "haversine_distance_km": np.random.uniform(50, 2500, n),
        "estimated_delivery_duration_days": np.random.uniform(10, 30, n),
        "max_product_weight_g": np.random.uniform(200, 5000, n),
        "total_product_volume_cm3": np.random.uniform(1000, 20000, n),
        "seller_historical_delay_rate": np.random.uniform(1, 20, n),
        "purchase_month": np.random.choice(range(1, 13), n),
        "purchase_dayofweek": np.random.choice(range(7), n),
        "purchase_hour": np.random.choice(range(24), n),
        "customer_state": np.random.choice(["SP", "RJ", "MG", "BA"], n),
        "seller_state": np.random.choice(["SP", "PR", "SC"], n),
        "is_interstate_shipment": np.random.choice([0, 1], n),
        "top_category_name": np.random.choice(["bed_bath_table", "health_beauty"], n),
        "primary_payment_type": np.random.choice(["credit_card", "boleto"], n),
        "is_delivered_late": np.random.choice([0, 1], n, p=[0.9, 0.1]),
    })
    test_df = train_df.copy()

    classifier = DeliveryRiskClassifier(random_state=42)
    fitted_model, metrics = classifier.fit(train_df, test_df)

    assert "roc_auc" in metrics
    assert "f1" in metrics

    # Single order prediction
    sample_order = train_df.iloc[0].to_dict()
    res = fitted_model.predict_risk(sample_order)
    assert res["risk_level"] in ["Low", "Medium", "High"]
    assert 0.0 <= res["delay_probability"] <= 1.0
    assert len(res["risk_factors"]) > 0


def test_satisfaction_review_risk():
    """Verify review risk model training and dissatisfaction driver explainability."""
    np.random.seed(42)
    n = 200
    train_df = pd.DataFrame({
        "total_delivery_duration_days": np.random.uniform(5, 35, n),
        "delivery_delay_vs_estimated_days": np.random.uniform(-10, 15, n),
        "freight_ratio_pct": np.random.uniform(5, 40, n),
        "total_items_price_brl": np.random.uniform(30, 400, n),
        "total_freight_value_brl": np.random.uniform(10, 60, n),
        "total_item_count": np.random.choice([1, 2], n),
        "haversine_distance_km": np.random.uniform(100, 1500, n),
        "seller_historical_review_score": np.random.uniform(3.0, 5.0, n),
        "is_delivered_late": np.random.choice([0, 1], n, p=[0.85, 0.15]),
        "primary_payment_type": ["credit_card"] * n,
        "customer_state": ["SP"] * n,
        "is_interstate_shipment": [0] * n,
        "top_category_name": ["telephony"] * n,
        "is_negative_review": np.random.choice([0, 1], n, p=[0.8, 0.2]),
    })
    test_df = train_df.copy()

    model = ReviewRiskClassifier(n_estimators=30, random_state=42)
    fitted_model, metrics = model.fit(train_df, test_df)

    assert "roc_auc" in metrics
    assert 0.0 <= metrics["roc_auc"] <= 1.0

    sample = train_df.iloc[0].to_dict()
    res = fitted_model.predict_risk(sample)
    assert res["negative_review_risk"] in ["Low", "Medium", "High"]
    assert 0.0 <= res["dissatisfaction_probability"] <= 1.0


def test_demand_forecasting_pipeline():
    """Verify autoregressive time-series forecast logic and confidence intervals."""
    dates = pd.date_range(start="2018-01-01", periods=100, freq="D")
    df_ts = pd.DataFrame({
        "order_date": dates,
        "daily_gmv": 50000 + 5000 * np.sin(np.linspace(0, 20, 100)) + np.random.normal(0, 2000, 100),
        "daily_orders": 300 + 30 * np.sin(np.linspace(0, 20, 100)) + np.random.normal(0, 15, 100)
    })

    forecaster = DemandForecaster(target_col="daily_gmv", horizon_days=14, random_state=42)
    fitted_model, eval_res = forecaster.fit(df_ts, split_date="2018-03-15")

    assert "ml_metrics" in eval_res
    assert "mae" in eval_res["ml_metrics"]

    horizon = fitted_model.forecast_horizon(steps=7)
    assert len(horizon) == 7
    for step in horizon:
        assert step["lower_bound"] <= step["forecast_value"] <= step["upper_bound"]
        assert step["forecast_value"] >= 0.0


def test_anomaly_detection_logic():
    """Verify rolling statistical anomaly detector flags simulated revenue spikes and drops."""
    dates = pd.date_range(start="2018-01-01", periods=60, freq="D")
    values = [40000.0] * 60
    # Inject significant spike at day 20 and drop at day 45 (well separated from window)
    values[20] = 120000.0
    values[45] = 2000.0

    df_ts = pd.DataFrame({
        "order_date": dates,
        "daily_gmv": values,
        "daily_orders": [250] * 60,
        "daily_late_rate": [5.0] * 60,
        "avg_order_value": [160.0] * 60
    })

    detector = BusinessAnomalyDetector(z_threshold=2.5, window_days=14)
    anomalies = detector.detect_anomalies(df_ts)

    assert len(anomalies) >= 2
    metrics_flagged = [a["metric"] for a in anomalies]
    assert "daily_gmv" in metrics_flagged
    severities = [a["severity"] for a in anomalies]
    assert any(s in ["Critical", "High"] for s in severities)
