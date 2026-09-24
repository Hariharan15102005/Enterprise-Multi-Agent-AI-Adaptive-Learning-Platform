"""Pipeline runner for Business Anomaly Detection execution."""

import logging
import json
from ml.data.data_extractor import DataExtractor
from ml.models.anomaly_detection.business_anomalies import BusinessAnomalyDetector
from ml.config.ml_config import ml_config

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("olistiq.ml.pipelines.anomaly_detection")


def run_pipeline() -> None:
    logger.info("=== Starting Business Anomaly Detection Run ===")
    
    extractor = DataExtractor()
    df_ts = extractor.get_time_series_data()
    
    detector = BusinessAnomalyDetector(
        z_threshold=ml_config.ANOMALY_Z_THRESHOLD,
        window_days=14
    )
    anomalies = detector.detect_anomalies(df_ts)
    
    output_path = ml_config.ARTIFACTS_PATH / "detected_anomalies.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(anomalies, f, indent=2)
        
    logger.info("Saved %d anomalies to %s", len(anomalies), output_path)


if __name__ == "__main__":
    run_pipeline()
