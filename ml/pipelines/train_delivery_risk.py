"""Pipeline runner for Delivery Delay Risk Classifier training and registration."""

import logging
import sys
import pandas as pd
from ml.data.data_extractor import DataExtractor
from ml.models.delivery_risk.delay_classifier import DeliveryRiskClassifier
from ml.registry.model_registry import model_registry
from ml.config.ml_config import ml_config

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("olistiq.ml.pipelines.delivery_risk")


def run_pipeline() -> None:
    logger.info("=== Starting Delivery Delay Risk Training Pipeline ===")
    
    # 1. Extract Data
    extractor = DataExtractor()
    df = extractor.get_delivery_risk_data()
    
    if len(df) == 0:
        logger.error("No order records found for delivery risk modeling.")
        sys.exit(1)
        
    # 2. Chronological Out-of-Time Train/Test Split (Avoid temporal data leakage)
    df["purchase_timestamp"] = pd.to_datetime(df["purchase_timestamp"])
    df = df.sort_values("purchase_timestamp").reset_index(drop=True)
    
    # Train on orders before 2018-05-01, Test on 2018-05-01 onwards
    split_date = "2018-05-01"
    df_train = df[df["purchase_timestamp"] < split_date].copy()
    df_test = df[df["purchase_timestamp"] >= split_date].copy()
    
    logger.info(
        "Chronological Split: %d Train samples (< %s), %d Test samples (>= %s)",
        len(df_train), split_date, len(df_test), split_date
    )
    
    # 3. Train Model
    classifier = DeliveryRiskClassifier(
        model_type=ml_config.DELIVERY_RISK_MODEL_TYPE,
        random_state=ml_config.RANDOM_SEED
    )
    fitted_model, eval_metrics = classifier.fit(df_train, df_test)
    
    # 4. Register in Model Registry
    artifact_path = model_registry.register_model(
        model_name="delivery_risk",
        version="v1.0",
        model_object=fitted_model,
        model_type=ml_config.DELIVERY_RISK_MODEL_TYPE,
        features=fitted_model.features,
        evaluation_metrics=eval_metrics,
        hyperparameters={
            "max_iter": ml_config.DELIVERY_MAX_ITER,
            "learning_rate": ml_config.DELIVERY_LEARNING_RATE,
            "min_samples_leaf": ml_config.DELIVERY_MIN_SAMPLES_LEAF,
            "class_weight": "balanced",
            "random_seed": ml_config.RANDOM_SEED,
            "split_type": "chronological_out_of_time",
            "split_date": split_date
        },
        description="Fulfillment delay risk classifier using pre-dispatch features and seller history.",
        status="active"
    )
    
    logger.info("Delivery Risk pipeline completed successfully! Saved: %s", artifact_path)
    logger.info("Test ROC-AUC: %s, PR-AUC: %s, F1: %s", eval_metrics.get("roc_auc"), eval_metrics.get("pr_auc"), eval_metrics.get("f1"))


if __name__ == "__main__":
    run_pipeline()
