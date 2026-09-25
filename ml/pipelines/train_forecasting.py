"""Pipeline runner for Demand & GMV Time Series Forecasting model training."""

import logging
import sys
from ml.data.data_extractor import DataExtractor
from ml.models.forecasting.demand_forecaster import DemandForecaster
from ml.registry.model_registry import model_registry
from ml.config.ml_config import ml_config

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("olistiq.ml.pipelines.forecasting")


def run_pipeline() -> None:
    logger.info("=== Starting Demand & GMV Forecasting Training Pipeline ===")
    
    # 1. Extract Data
    extractor = DataExtractor()
    df_ts = extractor.get_time_series_data()
    
    if len(df_ts) == 0:
        logger.error("No time series records found for forecasting.")
        sys.exit(1)
        
    # 2. Train GMV Forecaster
    logger.info("Training Daily GMV Forecaster...")
    gmv_forecaster = DemandForecaster(
        target_col="daily_gmv",
        horizon_days=ml_config.FORECAST_HORIZON_DAYS,
        random_state=ml_config.RANDOM_SEED
    )
    fitted_gmv, gmv_metrics = gmv_forecaster.fit(df_ts, split_date="2018-05-31")
    
    # 3. Train Orders Forecaster
    logger.info("Training Daily Order Volume Forecaster...")
    orders_forecaster = DemandForecaster(
        target_col="daily_orders",
        horizon_days=ml_config.FORECAST_HORIZON_DAYS,
        random_state=ml_config.RANDOM_SEED
    )
    fitted_orders, orders_metrics = orders_forecaster.fit(df_ts, split_date="2018-05-31")
    
    # Register GMV Forecaster
    model_registry.register_model(
        model_name="gmv_forecaster",
        version="v1.0",
        model_object=fitted_gmv,
        model_type="Ridge_Autoregressive_TimeSeries",
        features=fitted_gmv.feature_cols,
        evaluation_metrics=gmv_metrics,
        hyperparameters={"model": "Ridge", "alpha": 10.0, "scaler": "StandardScaler", "horizon_days": 30, "random_seed": ml_config.RANDOM_SEED},
        description="Daily Gross Merchandise Value (GMV) 30-day forecast engine using Ridge regression with 95% prediction intervals.",
        status="active"
    )
    
    # Register Orders Forecaster
    model_registry.register_model(
        model_name="orders_forecaster",
        version="v1.0",
        model_object=fitted_orders,
        model_type="Ridge_Autoregressive_TimeSeries",
        features=fitted_orders.feature_cols,
        evaluation_metrics=orders_metrics,
        hyperparameters={"model": "Ridge", "alpha": 10.0, "scaler": "StandardScaler", "horizon_days": 30, "random_seed": ml_config.RANDOM_SEED},
        description="Daily Order Volume 30-day forecast engine using Ridge regression with 95% prediction intervals.",
        status="active"
    )
    
    logger.info("Forecasting pipeline completed successfully for GMV and Orders!")


if __name__ == "__main__":
    run_pipeline()
