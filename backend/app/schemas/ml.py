"""Pydantic schemas and Data Contracts for OlistIQ ML API endpoints."""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


# ==========================================
# 1. Model Registry Schemas
# ==========================================
class ModelMetadataResponse(BaseModel):
    model_name: str
    version: str
    model_type: str
    status: str
    features: List[str]
    evaluation_metrics: Dict[str, Any]
    hyperparameters: Dict[str, Any]
    description: str
    created_at: str
    extra_metadata: Optional[Dict[str, Any]] = None


class ModelListResponse(BaseModel):
    total_models: int
    models: List[ModelMetadataResponse]


# ==========================================
# 2. Customer Segmentation Schemas
# ==========================================
class ClusterProfileSchema(BaseModel):
    segment_name: str
    description: str
    customer_count: int
    share_pct: float
    avg_recency_days: float
    avg_frequency: float
    avg_monetary_brl: float
    avg_order_value_brl: float
    avg_category_diversity: float


class SegmentsOverviewResponse(BaseModel):
    model_version: str
    model_type: str
    total_customers_analyzed: int
    silhouette_score: float
    n_clusters: int
    segments: List[ClusterProfileSchema]


class CustomerSegmentResponse(BaseModel):
    customer_unique_id: str
    customer_state: Optional[str] = None
    cluster_id: int
    segment_name: str
    description: str
    customer_metrics: Dict[str, Any]
    benchmark_comparison: Dict[str, Any]


# ==========================================
# 3. Delivery Delay Risk Schemas
# ==========================================
class DeliveryRiskRequest(BaseModel):
    total_items_price_brl: float = Field(..., json_schema_extra={"example": 120.50})
    total_freight_value_brl: float = Field(..., json_schema_extra={"example": 25.00})
    freight_ratio_pct: float = Field(..., json_schema_extra={"example": 17.18})
    total_item_count: int = Field(..., json_schema_extra={"example": 1})
    unique_product_count: int = Field(..., json_schema_extra={"example": 1})
    haversine_distance_km: float = Field(..., json_schema_extra={"example": 450.0})
    estimated_delivery_duration_days: float = Field(..., json_schema_extra={"example": 15.0})
    max_product_weight_g: float = Field(default=500.0, json_schema_extra={"example": 800.0})
    total_product_volume_cm3: float = Field(default=5000.0, json_schema_extra={"example": 6000.0})
    seller_historical_delay_rate: float = Field(default=5.0, json_schema_extra={"example": 7.5})
    purchase_month: int = Field(default=5, json_schema_extra={"example": 5})
    purchase_dayofweek: int = Field(default=2, json_schema_extra={"example": 2})
    purchase_hour: int = Field(default=14, json_schema_extra={"example": 14})
    customer_state: str = Field(default="SP", json_schema_extra={"example": "RJ"})
    seller_state: str = Field(default="SP", json_schema_extra={"example": "SP"})
    is_interstate_shipment: int = Field(default=1, json_schema_extra={"example": 1})
    top_category_name: str = Field(default="health_beauty", json_schema_extra={"example": "health_beauty"})
    primary_payment_type: str = Field(default="credit_card", json_schema_extra={"example": "credit_card"})


class RiskFactorSchema(BaseModel):
    factor: str
    detail: str
    severity: str


class DeliveryRiskResponse(BaseModel):
    order_id: Optional[str] = None
    risk_level: str
    delay_probability: float
    estimated_delivery_duration_days: Optional[float] = None
    risk_factors: List[RiskFactorSchema]
    model_version: str
    model_type: str


# ==========================================
# 4. Satisfaction / Review Risk Schemas
# ==========================================
class DissatisfactionDriverSchema(BaseModel):
    factor: str
    detail: str
    impact: str


class SatisfactionRiskResponse(BaseModel):
    order_id: str
    negative_review_risk: str
    dissatisfaction_probability: float
    predicted_satisfaction_status: str
    dissatisfaction_drivers: List[DissatisfactionDriverSchema]
    model_version: str


# ==========================================
# 5. Forecasting Schemas
# ==========================================
class ForecastPointSchema(BaseModel):
    date: str
    forecast_value: float
    lower_bound: float
    upper_bound: float
    day_name: str
    is_weekend: bool


class ForecastResponse(BaseModel):
    target_metric: str
    horizon_days: int
    unit: str
    model_version: str
    model_type: str
    evaluation_metrics: Dict[str, Any]
    forecast: List[ForecastPointSchema]


# ==========================================
# 6. Business Anomaly Schemas
# ==========================================
class AnomalyItemSchema(BaseModel):
    id: str
    metric: str
    metric_label: str
    date: str
    observed_value: float
    baseline_value: float
    deviation_pct: float
    z_score: float
    direction: str
    severity: str
    explanation: str


class AnomaliesResponse(BaseModel):
    total_anomalies: int
    anomalies: List[AnomalyItemSchema]
