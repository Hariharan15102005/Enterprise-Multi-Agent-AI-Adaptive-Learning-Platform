"""Pipeline runner for Customer RFM Segmentation model training and registration."""

import logging
import sys
from ml.data.data_extractor import DataExtractor
from ml.models.customer_segmentation.rfm_clustering import CustomerSegmentationModel
from ml.registry.model_registry import model_registry
from ml.config.ml_config import ml_config

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("olistiq.ml.pipelines.customer_segmentation")


def run_pipeline() -> None:
    logger.info("=== Starting Customer RFM Segmentation Training Pipeline ===")
    
    # 1. Extract Data
    extractor = DataExtractor()
    df = extractor.get_customer_segmentation_data()
    
    if len(df) == 0:
        logger.error("No customer records found for RFM training.")
        sys.exit(1)
        
    # 2. Train Model
    model = CustomerSegmentationModel(
        n_clusters=ml_config.RFM_N_CLUSTERS,
        random_state=ml_config.RANDOM_SEED
    )
    fitted_model, eval_metrics = model.fit(df)
    
    # 3. Register in Model Registry
    artifact_path = model_registry.register_model(
        model_name="customer_segmentation",
        version="v1.0",
        model_object=fitted_model,
        model_type="KMeans_Clustering",
        features=fitted_model.features,
        evaluation_metrics=eval_metrics,
        hyperparameters={
            "n_clusters": ml_config.RFM_N_CLUSTERS,
            "random_seed": ml_config.RANDOM_SEED,
            "init": "k-means++",
            "n_init": 10
        },
        description="RFM Customer Segmentation clustering engine on unique consumers.",
        status="active",
        extra_metadata={"cluster_profiles": fitted_model.cluster_profiles}
    )
    
    logger.info("Customer Segmentation pipeline completed successfully! Saved: %s", artifact_path)
    logger.info("Silhouette Score: %s", eval_metrics.get("silhouette_score"))


if __name__ == "__main__":
    run_pipeline()
