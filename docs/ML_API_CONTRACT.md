# OlistIQ ML API Contract & Frontend Integration Specification

Base URL: `/api/v1/ml`

---

## 1. List Models

**`GET /api/v1/ml/models`**

Returns registered ML models, active versions, and evaluation summaries.

### Response `200 OK`
```json
{
  "total_models": 4,
  "models": [
    {
      "model_name": "delivery_risk",
      "version": "v1.0",
      "model_type": "HistGradientBoosting",
      "status": "active",
      "features": ["total_items_price_brl", "haversine_distance_km", "..."],
      "evaluation_metrics": {
        "roc_auc": 0.7287,
        "pr_auc": 0.1295,
        "f1": 0.2145,
        "recall": 0.346
      },
      "hyperparameters": {"learning_rate": 0.08, "max_iter": 150},
      "description": "Fulfillment delay risk classifier using pre-dispatch features.",
      "created_at": "2026-09-24T15:55:14.570000"
    }
  ]
}
```

---

## 2. Customer Segmentation Overview

**`GET /api/v1/ml/segments`**

Returns overall customer clustering profiles, customer counts, and spend averages for dashboard charts.

### Response `200 OK`
```json
{
  "model_version": "v1.0",
  "model_type": "KMeans_Clustering",
  "total_customers_analyzed": 95420,
  "silhouette_score": 0.5127,
  "n_clusters": 4,
  "segments": [
    {
      "segment_name": "Champions & High-Value",
      "description": "Highest lifetime spend and strong engagement with recent purchases.",
      "customer_count": 2924,
      "share_pct": 3.06,
      "avg_recency_days": 285.2,
      "avg_frequency": 1.54,
      "avg_monetary_brl": 621.4,
      "avg_order_value_brl": 387.9,
      "avg_category_diversity": 2.1
    }
  ]
}
```

---

## 3. Individual Customer Segment & Explanation

**`GET /api/v1/ml/customers/{customer_unique_id}/segment`**

### Response `200 OK`
```json
{
  "customer_unique_id": "871766c5855e863f6ed8505a0ba3075c",
  "customer_state": "SP",
  "cluster_id": 0,
  "segment_name": "High-Value At-Risk",
  "description": "Historical big spenders who have not made a purchase recently.",
  "customer_metrics": {
    "recency_days": 290,
    "frequency_orders": 1,
    "monetary_spend_brl": 299.90
  },
  "benchmark_comparison": {
    "segment_avg_spend": 274.79,
    "segment_avg_recency": 287.6
  }
}
```

---

## 4. Delivery Risk for Existing Order

**`GET /api/v1/ml/delivery-risk/{order_id}`**

### Response `200 OK`
```json
{
  "order_id": "e481f51cbdc54678b7cc49136f2d6af7",
  "risk_level": "Low",
  "delay_probability": 0.0842,
  "estimated_delivery_duration_days": 15.4,
  "risk_factors": [
    {
      "factor": "Standard Local Delivery",
      "detail": "Normal distance and reliable seller profile.",
      "severity": "None"
    }
  ],
  "model_version": "v1.0",
  "model_type": "HistGradientBoosting"
}
```

---

## 5. Custom Checkout Delivery Risk Simulation

**`POST /api/v1/ml/delivery-risk/predict`**

### Request Body
```json
{
  "total_items_price_brl": 150.0,
  "total_freight_value_brl": 45.0,
  "freight_ratio_pct": 23.07,
  "total_item_count": 1,
  "unique_product_count": 1,
  "haversine_distance_km": 1450.0,
  "estimated_delivery_duration_days": 12.0,
  "max_product_weight_g": 2500.0,
  "total_product_volume_cm3": 12000.0,
  "seller_historical_delay_rate": 14.5,
  "purchase_month": 6,
  "purchase_dayofweek": 4,
  "purchase_hour": 16,
  "customer_state": "CE",
  "seller_state": "SP",
  "is_interstate_shipment": 1,
  "top_category_name": "bed_bath_table",
  "primary_payment_type": "credit_card"
}
```

### Response `200 OK`
```json
{
  "order_id": null,
  "risk_level": "High",
  "delay_probability": 0.7412,
  "estimated_delivery_duration_days": 12.0,
  "risk_factors": [
    {
      "factor": "Long Distance Transit",
      "detail": "Inter-regional shipment spanning 1450 km.",
      "severity": "High"
    },
    {
      "factor": "Seller SLA History",
      "detail": "Seller has a 14.5% historical breach rate.",
      "severity": "High"
    },
    {
      "factor": "Interstate Cross-Border Logistics",
      "detail": "Crosses state lines from SP to CE.",
      "severity": "Medium"
    }
  ],
  "model_version": "v1.0",
  "model_type": "HistGradientBoosting"
}
```

---

## 6. Time Series Demand & GMV Forecast

**`GET /api/v1/ml/forecast?target=daily_gmv&horizon_days=30`**

### Response `200 OK`
```json
{
  "target_metric": "daily_gmv",
  "horizon_days": 30,
  "unit": "BRL",
  "model_version": "v1.0",
  "model_type": "GradientBoostingRegressor_LagAutoregressive",
  "evaluation_metrics": {
    "mae_improvement_pct": 23.2,
    "ml_metrics": {
      "mae": 5998.72,
      "rmse": 7450.31,
      "r2_score": 0.462
    }
  },
  "forecast": [
    {
      "date": "2018-09-01",
      "forecast_value": 48250.30,
      "lower_bound": 33647.69,
      "upper_bound": 62852.91,
      "day_name": "Saturday",
      "is_weekend": true
    }
  ]
}
```

---

## 7. Business Anomalies Stream

**`GET /api/v1/ml/anomalies?limit=10`**

### Response `200 OK`
```json
{
  "total_anomalies": 25,
  "anomalies": [
    {
      "id": "anom_daily_gmv_2017-11-24",
      "metric": "daily_gmv",
      "metric_label": "Gross Merchandise Value (GMV)",
      "date": "2017-11-24",
      "observed_value": 158420.50,
      "baseline_value": 42150.20,
      "deviation_pct": 275.8,
      "z_score": 5.42,
      "direction": "Spike",
      "severity": "Critical",
      "explanation": "High-revenue surge (+275.8% vs 14-day baseline) driven by promotion or seasonal campaign (Black Friday 2017)."
    }
  ]
}
```
