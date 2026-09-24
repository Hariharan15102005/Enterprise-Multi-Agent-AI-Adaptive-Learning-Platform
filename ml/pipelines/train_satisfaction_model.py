"""Pipeline runner for Customer Satisfaction / Review Risk model training and registration."""

import logging
import sys
import pandas as pd
from ml.data.data_extractor import DataExtractor
from ml.models.satisfaction.review_risk import ReviewRiskClassifier
from ml.registry.model_registry import model_registry
from ml.config.ml_config import ml_config

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("olistiq.ml.pipelines.satisfaction")


def run_pipeline() -> None:
    logger.info("=== Starting Customer Satisfaction / Review Risk Training Pipeline ===")
    
    # 1. Extract Data
    extractor = DataExtractor()
    df = extractor.get_satisfaction_data()
    
    if len(df) == 0:
        logger.error("No review records found for satisfaction modeling.")
        sys.exit(1)
        
    # 2. Chronological Train/Test Split
    df["purchase_timestamp"] = pd.to_datetime(df["purchase_timestamp"])
    df = df.sort_values("purchase_timestamp").reset_index(drop=True)
    
    split_date = "2018-05-01"
    df_train = df[df["purchase_timestamp"] < split_date].copy()
    df_test = df[df["purchase_timestamp"] >= split_date].copy()
    
    logger.info(
        "Chronological Split: %d Train samples (< %s), %d Test samples (>= %s)",
        len(df_train), split_date, len(df_test), split_date
    )
    
    # 3. Train Model
    classifier = ReviewRiskClassifier(
        n_estimators=100,
        random_state=ml_config.RANDOM_SEED
    )
    fitted_model, eval_metrics = classifier.fit(df_train, df_test)
    
    # 4. Register in Model Registry
    artifact_path = model_registry.register_model(
        model_name="satisfaction_risk",
        version="v1.0",
        model_object=fitted_model,
        model_type="RandomForestClassifier",
        features=fitted_model.features,
        evaluation_metrics=eval_metrics,
        hyperparameters={
            "n_estimators": 100,
            "max_depth": 10,
            "class_weight": "balanced",
            "random_seed": ml_config.RANDOM_SEED,
            "split_type": "chronological_out_of_time",
            "split_date": split_date
        },
        description="Predicts risk of low review scores (1-2 stars) from operational fulfillment variables.",
        status="active"
    )
    
    logger.info("Satisfaction Risk pipeline completed successfully! Saved: %s", artifact_path)
    logger.info("Test ROC-AUC: %s, PR-AUC: %s, F1: %s", eval_metrics.get("roc_auc"), eval_metrics.get("pr_auc"), eval_metrics.get("f1"))


if __name__ == "__main__":
    run_pipeline()
