"""Integration tests for FastAPI ML API endpoints."""

import pytest
import anyio
import httpx
from sqlalchemy import text
from backend.app.main import app
from database.connection import engine


@pytest.fixture
def anyio_backend():
    return 'asyncio'


@pytest.mark.anyio
async def test_list_models_endpoint():
    """Verify GET /api/v1/ml/models returns registered models and schemas."""
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/ml/models")
        assert response.status_code == 200
        data = response.json()
        assert "total_models" in data
        assert data["total_models"] >= 4
        model_names = [m["model_name"] for m in data["models"]]
        assert "customer_segmentation" in model_names
        assert "delivery_risk" in model_names
        assert "satisfaction_risk" in model_names
        assert "gmv_forecaster" in model_names


@pytest.mark.anyio
async def test_model_details_endpoint():
    """Verify GET /api/v1/ml/models/{model_name} returns metadata and 404 on invalid."""
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/ml/models/delivery_risk")
        assert response.status_code == 200
        data = response.json()
        assert data["model_name"] == "delivery_risk"
        assert "evaluation_metrics" in data
        assert "features" in data

        # 404 test
        not_found = await client.get("/api/v1/ml/models/non_existent_model")
        assert not_found.status_code == 404


@pytest.mark.anyio
async def test_segments_overview_endpoint():
    """Verify GET /api/v1/ml/segments returns cluster distribution and profiles."""
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/ml/segments")
        assert response.status_code == 200
        data = response.json()
        assert "segments" in data
        assert len(data["segments"]) >= 3
        assert "silhouette_score" in data
        assert data["total_customers_analyzed"] > 0


@pytest.mark.anyio
async def test_customer_segment_individual_endpoint():
    """Verify GET /api/v1/ml/customers/{customer_unique_id}/segment with valid and invalid IDs."""
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        cust_res = await client.get("/api/v1/customers/list?page=1&page_size=1")
        assert cust_res.status_code == 200
        customers = cust_res.json()["data"]
        assert len(customers) > 0
        test_cid = customers[0]["customer_unique_id"]

        response = await client.get(f"/api/v1/ml/customers/{test_cid}/segment")
        assert response.status_code == 200
        data = response.json()
        assert data["customer_unique_id"] == test_cid
        assert "cluster_id" in data
        assert "segment_name" in data
        assert "benchmark_comparison" in data

        # 404 test for non-existent customer
        invalid_res = await client.get("/api/v1/ml/customers/invalid_uuid_99999/segment")
        assert invalid_res.status_code == 404


@pytest.mark.anyio
async def test_delivery_risk_custom_prediction():
    """Verify POST /api/v1/ml/delivery-risk/predict with arbitrary checkout payload."""
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        payload = {
            "total_items_price_brl": 150.0,
            "total_freight_value_brl": 35.0,
            "freight_ratio_pct": 18.9,
            "total_item_count": 1,
            "unique_product_count": 1,
            "haversine_distance_km": 1200.0,
            "estimated_delivery_duration_days": 18.0,
            "max_product_weight_g": 1200.0,
            "total_product_volume_cm3": 8000.0,
            "seller_historical_delay_rate": 12.5,
            "purchase_month": 6,
            "purchase_dayofweek": 3,
            "purchase_hour": 15,
            "customer_state": "BA",
            "seller_state": "SP",
            "is_interstate_shipment": 1,
            "top_category_name": "bed_bath_table",
            "primary_payment_type": "credit_card"
        }
        response = await client.post("/api/v1/ml/delivery-risk/predict", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "risk_level" in data
        assert data["risk_level"] in ["Low", "Medium", "High"]
        assert 0.0 <= data["delay_probability"] <= 1.0
        assert len(data["risk_factors"]) > 0


@pytest.mark.anyio
async def test_delivery_risk_order_endpoint():
    """Verify GET /api/v1/ml/delivery-risk/{order_id}."""
    with engine.connect() as conn:
        order_row = conn.execute(text("SELECT order_id FROM fact_orders WHERE order_status = 'delivered' LIMIT 1")).fetchone()
    
    assert order_row is not None
    test_oid = order_row[0]

    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(f"/api/v1/ml/delivery-risk/{test_oid}")
        assert response.status_code == 200
        data = response.json()
        assert data["order_id"] == test_oid
        assert "risk_level" in data
        assert "delay_probability" in data
        assert len(data["risk_factors"]) > 0


@pytest.mark.anyio
async def test_satisfaction_risk_endpoint():
    """Verify GET /api/v1/ml/satisfaction-risk/{order_id}."""
    with engine.connect() as conn:
        order_row = conn.execute(text("SELECT order_id FROM fact_orders WHERE order_status = 'delivered' LIMIT 1")).fetchone()
    
    test_oid = order_row[0]
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(f"/api/v1/ml/satisfaction-risk/{test_oid}")
        assert response.status_code == 200
        data = response.json()
        assert data["order_id"] == test_oid
        assert "negative_review_risk" in data
        assert "dissatisfaction_probability" in data
        assert "predicted_satisfaction_status" in data


@pytest.mark.anyio
async def test_forecasting_endpoint():
    """Verify GET /api/v1/ml/forecast for daily_gmv and daily_orders."""
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        # GMV forecast
        res_gmv = await client.get("/api/v1/ml/forecast?target=daily_gmv&horizon_days=14")
        assert res_gmv.status_code == 200
        data_gmv = res_gmv.json()
        assert data_gmv["target_metric"] == "daily_gmv"
        assert len(data_gmv["forecast"]) == 14
        assert data_gmv["unit"] == "BRL"
        assert "evaluation_metrics" in data_gmv

        # Orders forecast
        res_orders = await client.get("/api/v1/ml/forecast?target=daily_orders&horizon_days=7")
        assert res_orders.status_code == 200
        data_orders = res_orders.json()
        assert data_orders["target_metric"] == "daily_orders"
        assert len(data_orders["forecast"]) == 7

        # Bad request on invalid target
        bad_res = await client.get("/api/v1/ml/forecast?target=unsupported_target")
        assert bad_res.status_code == 400


@pytest.mark.anyio
async def test_anomalies_endpoint():
    """Verify GET /api/v1/ml/anomalies with optional filters."""
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/ml/anomalies?limit=10")
        assert response.status_code == 200
        data = response.json()
        assert "total_anomalies" in data
        assert "anomalies" in data
        assert len(data["anomalies"]) <= 10

        if data["total_anomalies"] > 0:
            anom = data["anomalies"][0]
            assert "observed_value" in anom
            assert "baseline_value" in anom
            assert "z_score" in anom
            assert "severity" in anom
            assert "explanation" in anom
