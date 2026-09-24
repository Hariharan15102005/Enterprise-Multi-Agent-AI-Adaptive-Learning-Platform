import pytest
import anyio
import httpx
from backend.app.main import app

@pytest.fixture
def anyio_backend():
    return 'asyncio'

@pytest.mark.anyio
async def test_health_endpoint():
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "service" in data

@pytest.mark.anyio
async def test_openapi_and_docs():
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        docs_resp = await client.get("/docs")
        assert docs_resp.status_code == 200
        openapi_resp = await client.get("/openapi.json")
        assert openapi_resp.status_code == 200
        schema = openapi_resp.json()
        assert "paths" in schema
        assert "/api/v1/dashboard/kpis" in schema["paths"]

@pytest.mark.anyio
async def test_dashboard_kpis_endpoint():
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/dashboard/kpis")
        assert response.status_code == 200
        res = response.json()
        assert res["success"] is True
        data = res["data"]
        assert data["total_orders"] > 90000
        assert data["gross_merchandise_value"] > 1000000.0
        assert data["on_time_delivery_rate"] > 80.0
        assert data["average_review_score"] > 3.5

@pytest.mark.anyio
async def test_dashboard_summary_endpoint():
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/dashboard/summary")
        assert response.status_code == 200
        res = response.json()
        assert res["success"] is True
        assert "kpis" in res["data"]
        assert "top_selling_category" in res["data"]

@pytest.mark.anyio
async def test_analytics_revenue_trends():
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/analytics/revenue?interval=month")
        assert response.status_code == 200
        res = response.json()
        assert res["success"] is True
        data = res["data"]
        assert len(data) > 10
        assert "gmv" in data[0]
        assert "order_count" in data[0]

@pytest.mark.anyio
async def test_analytics_categories():
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/analytics/categories?limit=5")
        assert response.status_code == 200
        res = response.json()
        assert res["success"] is True
        assert len(res["data"]) <= 5
        assert "category_name_en" in res["data"][0]

@pytest.mark.anyio
async def test_analytics_payments():
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/analytics/payments")
        assert response.status_code == 200
        res = response.json()
        assert res["success"] is True
        assert len(res["data"]) >= 4

@pytest.mark.anyio
async def test_analytics_insights():
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/analytics/insights")
        assert response.status_code == 200
        res = response.json()
        assert res["success"] is True
        assert len(res["data"]) >= 3

@pytest.mark.anyio
async def test_customer_segments():
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/customers/segments")
        assert response.status_code == 200
        res = response.json()
        assert res["success"] is True
        assert len(res["data"]) >= 3

@pytest.mark.anyio
async def test_customer_geo():
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/customers/geo")
        assert response.status_code == 200
        res = response.json()
        assert res["success"] is True
        assert len(res["data"]) >= 20

@pytest.mark.anyio
async def test_customer_list_pagination():
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/customers/list?page=1&page_size=10")
        assert response.status_code == 200
        res = response.json()
        assert res["success"] is True
        assert len(res["data"]) == 10
        assert res["metadata"]["page"] == 1
        assert res["metadata"]["total_records"] > 90000

@pytest.mark.anyio
async def test_products_list_pagination():
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/products/list?page=1&page_size=5")
        assert response.status_code == 200
        res = response.json()
        assert res["success"] is True
        assert len(res["data"]) == 5
        assert res["metadata"]["total_records"] == 32951

@pytest.mark.anyio
async def test_sellers_leaderboard():
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/sellers/leaderboard?page=1&page_size=10")
        assert response.status_code == 200
        res = response.json()
        assert res["success"] is True
        assert len(res["data"]) == 10
        assert res["metadata"]["total_records"] == 3095

@pytest.mark.anyio
async def test_logistics_overview():
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/logistics/overview")
        assert response.status_code == 200
        res = response.json()
        assert res["success"] is True
        data = res["data"]
        assert data["avg_delivery_days"] > 0
        assert data["on_time_delivery_rate"] > 0

@pytest.mark.anyio
async def test_logistics_by_state():
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/logistics/by-state")
        assert response.status_code == 200
        res = response.json()
        assert res["success"] is True
        assert len(res["data"]) >= 20

@pytest.mark.anyio
async def test_data_quality_overview():
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/data-quality/overview")
        assert response.status_code == 200
        res = response.json()
        assert res["success"] is True
        data = res["data"]
        assert data["overall_quality_score"] == 100.0
        assert data["status"] == "HEALTHY"
        assert data["tables_monitored"] == 9

@pytest.mark.anyio
async def test_invalid_parameters_validation():
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/customers/list?page_size=0")
        assert response.status_code == 422
        err = response.json()
        assert err["success"] is False
        assert err["error"]["code"] == "VALIDATION_ERROR"
