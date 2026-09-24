"""Master pipeline orchestrator to train and register all OlistIQ ML models."""

import logging
from ml.pipelines.train_customer_segmentation import run_pipeline as train_segmentation
from ml.pipelines.train_delivery_risk import run_pipeline as train_delivery
from ml.pipelines.train_satisfaction_model import run_pipeline as train_satisfaction
from ml.pipelines.train_forecasting import run_pipeline as train_forecast
from ml.pipelines.run_anomaly_detection import run_pipeline as run_anomalies

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("olistiq.ml.pipelines.master")


def train_all() -> None:
    logger.info("==================================================")
    logger.info("  OLISTIQ ML PIPELINE: TRAINING & REGISTRATION   ")
    logger.info("==================================================")
    
    # 1. Customer RFM Segmentation
    train_segmentation()
    
    # 2. Delivery Delay Risk Classifier
    train_delivery()
    
    # 3. Customer Satisfaction / Review Risk Classifier
    train_satisfaction()
    
    # 4. Demand & GMV Forecasters
    train_forecast()
    
    # 5. Anomaly Detection
    run_anomalies()
    
    logger.info("==================================================")
    logger.info("  ALL OLISTIQ ML MODELS TRAINED & REGISTERED!     ")
    logger.info("==================================================")


if __name__ == "__main__":
    train_all()
