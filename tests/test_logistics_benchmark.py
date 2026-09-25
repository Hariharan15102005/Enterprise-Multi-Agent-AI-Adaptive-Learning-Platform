import pytest
import httpx
from backend.app.main import app
from backend.app.repositories.logistics_repository import LogisticsRepository, BRAZILIAN_STATES_MAP, derive_logistics_status
from backend.app.db.session import SessionLocal

@pytest.fixture
def anyio_backend():
    return 'asyncio'

@pytest.fixture(scope="module")
def db_session():
    db = SessionLocal()
    yield db
    db.close()

def test_status_derivation_logic():
    # Insufficient data
    assert derive_logistics_status(None, 10.0, 50) == "Insufficient data"
    assert derive_logistics_status(95.0, None, 50) == "Insufficient data"
    assert derive_logistics_status(95.0, 10.0, 5) == "Insufficient data"
    
    # Optimal: on_time >= 92% and speed <= 13d
    assert derive_logistics_status(94.1, 8.8, 40000) == "Optimal"
    assert derive_logistics_status(92.0, 13.0, 500) == "Optimal"
    
    # Good: on_time >= 88% and speed <= 18d
    assert derive_logistics_status(91.8, 15.6, 2000) == "Good"
    assert derive_logistics_status(88.5, 17.5, 1000) == "Good"
    
    # Moderate: on_time >= 80% and speed <= 24d
    assert derive_logistics_status(86.5, 15.3, 12000) == "Moderate"
    assert derive_logistics_status(80.5, 21.6, 700) == "Moderate"
    
    # High SLA Risk: on_time < 80% or speed > 24d
    assert derive_logistics_status(76.1, 24.5, 400) == "High SLA Risk"
    assert derive_logistics_status(95.9, 26.4, 150) == "High SLA Risk"
    assert derive_logistics_status(87.8, 29.4, 40) == "High SLA Risk"

def test_brazil_states_map():
    assert len(BRAZILIAN_STATES_MAP) == 27
    assert BRAZILIAN_STATES_MAP["SP"] == "São Paulo"
    assert BRAZILIAN_STATES_MAP["RJ"] == "Rio de Janeiro"
    assert BRAZILIAN_STATES_MAP["DF"] == "Distrito Federal"

def test_logistics_repository_data_correctness(db_session):
    repo = LogisticsRepository(db_session)
    state_metrics = repo.get_logistics_by_state()
    
    # Verify all 27 states are returned
    assert len(state_metrics) == 27
    
    total_volume = sum(s["delivered_volume"] for s in state_metrics)
    assert total_volume == 96478  # Exact delivered order count
    
    # Verify SP values
    sp = next(s for s in state_metrics if s["state_code"] == "SP")
    assert sp["state_name"] == "São Paulo"
    assert sp["delivered_volume"] == 40505
    assert 8.0 < sp["avg_delivery_days"] < 10.0
    assert 93.0 < sp["on_time_rate"] < 96.0
    assert 16.0 < sp["avg_freight_cost"] < 19.0
    assert sp["logistics_status"] == "Optimal"
    
    # Verify diversity of values across states (no identical dummy values)
    volumes = set(s["delivered_volume"] for s in state_metrics)
    assert len(volumes) == 27  # All 27 states have distinct volumes
    
    speeds = set(s["avg_delivery_days"] for s in state_metrics)
    assert len(speeds) > 15  # Distinct real delivery days
    
    freights = set(s["avg_freight_cost"] for s in state_metrics)
    assert len(freights) > 20  # Distinct freight averages

@pytest.mark.anyio
async def test_logistics_by_state_api_endpoint():
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/logistics/by-state")
        assert response.status_code == 200
        res = response.json()
        assert res["success"] is True
        data = res["data"]
        assert len(data) == 27
        
        # Check contract fields
        for row in data:
            assert "state_code" in row
            assert "state_name" in row
            assert "delivered_volume" in row
            assert "avg_delivery_days" in row
            assert "on_time_rate" in row
            assert "avg_freight_cost" in row
            assert "logistics_status" in row
            assert row["delivered_volume"] > 0
            assert row["avg_delivery_days"] > 0
            assert 0 <= row["on_time_rate"] <= 100
            assert row["avg_freight_cost"] > 0
            assert row["logistics_status"] in ["Optimal", "Good", "Moderate", "High SLA Risk", "Insufficient data"]
