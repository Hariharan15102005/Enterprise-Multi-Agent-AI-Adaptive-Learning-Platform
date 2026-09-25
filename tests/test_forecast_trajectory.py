import pytest
import httpx
import numpy as np
import pandas as pd
from backend.app.main import app
from ml.data.data_extractor import DataExtractor
from ml.models.forecasting.demand_forecaster import DemandForecaster

@pytest.fixture
def anyio_backend():
    return 'asyncio'

def test_time_series_data_extraction():
    extractor = DataExtractor()
    df_ts = extractor.get_time_series_data()
    
    assert len(df_ts) >= 500
    assert "order_date" in df_ts.columns
    assert "daily_gmv" in df_ts.columns
    assert "daily_orders" in df_ts.columns
    
    # Chronological sort check
    dates = pd.to_datetime(df_ts["order_date"])
    assert dates.is_monotonic_increasing
    
    # Positive business values
    assert (df_ts["daily_gmv"] >= 0).all()
    assert (df_ts["daily_orders"] >= 0).all()

def test_ridge_forecaster_training_and_intervals():
    extractor = DataExtractor()
    df_ts = extractor.get_time_series_data()
    
    # Test GMV Forecaster
    gmv_forecaster = DemandForecaster(target_col="daily_gmv", horizon_days=30)
    fitted_gmv, gmv_metrics = gmv_forecaster.fit(df_ts, split_date="2018-05-31")
    
    assert gmv_metrics["model_type"] == "Ridge_Autoregressive_TimeSeries"
    assert gmv_metrics["ml_metrics"]["mae"] < gmv_metrics["baseline_metrics"]["mae"]
    assert gmv_metrics["ml_metrics"]["r2_score"] > 0.5
    
    forecast_30d = fitted_gmv.forecast_horizon(steps=30)
    assert len(forecast_30d) == 30
    
    # Verify bounds and ordering
    for pt in forecast_30d:
        assert pt["forecast_value"] >= 0
        assert pt["lower_bound"] >= 0
        assert pt["lower_bound"] <= pt["forecast_value"]
        assert pt["upper_bound"] >= pt["forecast_value"]
        assert pt["forecast_date"] == pt["date"]
        assert pt["predicted_value"] == pt["forecast_value"]
        assert pt["predicted_lower"] == pt["lower_bound"]
        assert pt["predicted_upper"] == pt["upper_bound"]
        assert pt["day_name"] in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

@pytest.mark.anyio
async def test_fastapi_forecast_endpoints():
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        # 1. 30-Day GMV Forecast
        res_gmv = await client.get("/api/v1/ml/forecast?target=daily_gmv&horizon_days=30")
        assert res_gmv.status_code == 200
        data_gmv = res_gmv.json()
        assert data_gmv["target_metric"] == "daily_gmv"
        assert data_gmv["horizon_days"] == 30
        assert data_gmv["unit"] == "BRL"
        assert "Ridge" in data_gmv["model_type"]
        assert len(data_gmv["forecast"]) == 30
        assert data_gmv["total_forecast"] > 0
        assert data_gmv["avg_daily_forecast"] > 0
        
        # 2. 30-Day Orders Forecast
        res_ord = await client.get("/api/v1/ml/forecast?target=daily_orders&horizon_days=30")
        assert res_ord.status_code == 200
        data_ord = res_ord.json()
        assert data_ord["target_metric"] == "daily_orders"
        assert data_ord["horizon_days"] == 30
        assert data_ord["unit"] == "orders"
        assert "Ridge" in data_ord["model_type"]
        assert len(data_ord["forecast"]) == 30
        assert data_ord["total_forecast"] > 0
        assert data_ord["avg_daily_forecast"] > 0
        
        # 3. Validation error on unsupported target
        res_bad = await client.get("/api/v1/ml/forecast?target=invalid_kpi")
        assert res_bad.status_code == 400
