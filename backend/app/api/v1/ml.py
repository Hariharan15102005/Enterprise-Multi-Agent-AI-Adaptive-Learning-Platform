"""FastAPI router for Machine Learning & Predictive Intelligence endpoints."""

import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, Query, Path

from backend.app.schemas.ml import (
    ModelListResponse,
    ModelMetadataResponse,
    SegmentsOverviewResponse,
    CustomerSegmentResponse,
    DeliveryRiskRequest,
    DeliveryRiskResponse,
    SatisfactionRiskResponse,
    ForecastResponse,
    AnomaliesResponse,
)
from ml.inference.ml_inference_service import ml_service

logger = logging.getLogger("olistiq.api.ml")
router = APIRouter(prefix="/ml", tags=["Machine Learning & Predictive Intelligence"])


@router.get("/models", response_model=ModelListResponse)
def list_models():
    """Lists all registered ML models with active version metadata and evaluation metrics."""
    models = ml_service.list_models()
    return {"total_models": len(models), "models": models}


@router.get("/models/{model_name}", response_model=ModelMetadataResponse)
def get_model_details(model_name: str = Path(..., description="Unique model identifier")):
    """Returns comprehensive metadata, feature schema, and evaluation metrics for a specific model."""
    meta = ml_service.get_model_details(model_name)
    if not meta:
        raise HTTPException(status_code=404, detail=f"Model '{model_name}' not found in registry.")
    return meta


@router.get("/segments", response_model=SegmentsOverviewResponse)
def get_customer_segments_overview():
    """Returns customer RFM cluster profiles, volume distribution, and spend benchmarks."""
    try:
        return ml_service.get_customer_segments_summary()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/customers/{customer_unique_id}/segment", response_model=CustomerSegmentResponse)
def get_customer_segment(customer_unique_id: str = Path(..., description="Unique customer UUID")):
    """Classifies a customer into an RFM segment with personalized benchmark comparison."""
    try:
        return ml_service.predict_customer_segment(customer_unique_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/delivery-risk/predict", response_model=DeliveryRiskResponse)
def predict_delivery_risk_custom(request: DeliveryRiskRequest):
    """Predicts delivery delay risk and root factors for arbitrary checkout parameters."""
    try:
        return ml_service.predict_delivery_risk(request.model_dump())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/delivery-risk/{order_id}", response_model=DeliveryRiskResponse)
def get_order_delivery_risk(order_id: str = Path(..., description="Unique Order ID")):
    """Calculates fulfillment delay risk and actionable drivers for an existing order."""
    try:
        return ml_service.predict_delivery_risk_for_order(order_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/satisfaction-risk/{order_id}", response_model=SatisfactionRiskResponse)
def get_order_satisfaction_risk(order_id: str = Path(..., description="Unique Order ID")):
    """Evaluates customer dissatisfaction risk and operational fulfillment drivers for an order."""
    try:
        return ml_service.predict_satisfaction_risk_for_order(order_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/forecast", response_model=ForecastResponse)
def get_forecast(
    target: str = Query("daily_gmv", description="Target metric: 'daily_gmv' or 'daily_orders'"),
    horizon_days: int = Query(30, ge=1, le=90, description="Forward forecast horizon in days")
):
    """Returns forward multi-step demand/GMV forecast with 95% confidence intervals."""
    if target not in ["daily_gmv", "daily_orders"]:
        raise HTTPException(status_code=400, detail="Target metric must be either 'daily_gmv' or 'daily_orders'.")
    try:
        return ml_service.get_forecast(target=target, horizon_days=horizon_days)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/anomalies", response_model=AnomaliesResponse)
def get_business_anomalies(
    metric: Optional[str] = Query(None, description="Filter by metric name"),
    severity: Optional[str] = Query(None, description="Filter by severity: Critical, High, Moderate"),
    limit: int = Query(50, ge=1, le=200, description="Maximum anomalies to return")
):
    """Returns detected historical and operational anomalies across core business KPIs."""
    try:
        return ml_service.get_anomalies(metric=metric, severity=severity, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
