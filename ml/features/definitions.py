"""Feature definitions and schema constants for OlistIQ ML models.

Contains strict feature lists, categorical/numerical splits, and leakage prevention rules.
"""

from typing import List

# ==========================================
# 1. Customer RFM Segmentation Features
# ==========================================
RFM_FEATURES: List[str] = [
    "recency_days",
    "frequency_orders",
    "monetary_spend_brl",
    "avg_order_value",
    "avg_items_per_order",
    "category_diversity",
]

# ==========================================
# 2. Delivery Delay Risk Features
# ==========================================
# STRICT LEAKAGE RULE:
# Features available ONLY at order approval/dispatch planning time.
# NEVER include: order_delivered_carrier_date, order_delivered_customer_date,
# carrier_transit_days, actual_delivery_duration_days.
DELIVERY_RISK_NUMERICAL_FEATURES: List[str] = [
    "total_items_price_brl",
    "total_freight_value_brl",
    "freight_ratio_pct",
    "total_item_count",
    "unique_product_count",
    "haversine_distance_km",
    "estimated_delivery_duration_days",
    "max_product_weight_g",
    "total_product_volume_cm3",
    "seller_historical_delay_rate",
    "purchase_month",
    "purchase_dayofweek",
    "purchase_hour",
]

DELIVERY_RISK_CATEGORICAL_FEATURES: List[str] = [
    "customer_state",
    "seller_state",
    "is_interstate_shipment",
    "top_category_name",
    "primary_payment_type",
]

DELIVERY_RISK_FEATURES: List[str] = DELIVERY_RISK_NUMERICAL_FEATURES + DELIVERY_RISK_CATEGORICAL_FEATURES

# ==========================================
# 3. Customer Satisfaction (Review Risk) Features
# ==========================================
# Target: is_negative_review (review_score <= 2)
# STRICT LEAKAGE RULE:
# Features available at fulfillment completion/post-delivery state.
# NEVER include: review_score, review_comment_title, review_comment_message,
# review_creation_timestamp, review_answer_timestamp.
SATISFACTION_NUMERICAL_FEATURES: List[str] = [
    "total_delivery_duration_days",
    "delivery_delay_vs_estimated_days",
    "freight_ratio_pct",
    "total_items_price_brl",
    "total_freight_value_brl",
    "total_item_count",
    "haversine_distance_km",
    "seller_historical_review_score",
]

SATISFACTION_CATEGORICAL_FEATURES: List[str] = [
    "is_delivered_late",
    "is_interstate_shipment",
    "primary_payment_type",
    "top_category_name",
    "customer_state",
]

SATISFACTION_FEATURES: List[str] = SATISFACTION_NUMERICAL_FEATURES + SATISFACTION_CATEGORICAL_FEATURES

# ==========================================
# 4. Forecasting Series Targets & Granularities
# ==========================================
FORECAST_TARGETS = ["daily_gmv", "daily_orders"]
