"""Integration tests for Phase 7 API Refinement, Global Error Handling, and CORS."""

import pytest
import anyio
import httpx
from backend.app.main import app


@pytest.fixture
def anyio_backend():
    return 'asyncio'


@pytest.mark.anyio
async def test_global_validation_error_format():
    """Verify validation errors return standard structured JSON schema."""
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        # Pass negative page size to trigger validation failure
        response = await client.get("/api/v1/customers/list?page_size=-5")
        assert response.status_code == 422
        data = response.json()
        assert data["success"] is False
        assert data["error"]["code"] == "VALIDATION_ERROR"
        assert "details" in data["error"]
        assert "errors" in data["error"]["details"]
        assert len(data["error"]["details"]["errors"]) > 0


@pytest.mark.anyio
async def test_process_time_header():
    """Verify X-Process-Time-Ms header is present on all API responses."""
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        assert "x-process-time-ms" in response.headers
        latency = float(response.headers["x-process-time-ms"])
        assert latency >= 0.0


@pytest.mark.anyio
async def test_cors_headers():
    """Verify CORS headers respond correctly to frontend origins."""
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        headers = {"Origin": "http://localhost:5173"}
        response = await client.get("/health", headers=headers)
        assert response.status_code == 200
        assert response.headers.get("access-control-allow-origin") == "http://localhost:5173"
        assert response.headers.get("access-control-allow-credentials") == "true"


@pytest.mark.anyio
async def test_resource_not_found_standard_error():
    """Verify 404 endpoints return standardized error schema."""
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/ml/models/non_existent_model_id")
        assert response.status_code == 404
        data = response.json()
        assert data["success"] is False
        assert data["error"]["code"] == "NOT_FOUND"
        assert "non_existent_model_id" in data["error"]["message"]


@pytest.mark.anyio
async def test_openapi_schema_completeness():
    """Verify OpenAPI specification contains documentation for all routes and tags."""
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/openapi.json")
        assert response.status_code == 200
        openapi = response.json()
        assert "paths" in openapi
        assert "info" in openapi
        assert openapi["info"]["title"] == "OlistIQ Decision Intelligence API"
        
        # Verify key routers are registered in paths
        paths = openapi["paths"]
        assert "/api/v1/dashboard/kpis" in paths
        assert "/api/v1/analytics/revenue" in paths
        assert "/api/v1/customers/list" in paths
        assert "/api/v1/ml/models" in paths
        assert "/api/v1/ai/query" in paths
        assert "/health" in paths
