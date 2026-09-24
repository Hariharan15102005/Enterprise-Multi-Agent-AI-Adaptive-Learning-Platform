from pathlib import Path
from dataclasses import dataclass
from config.settings import settings

BASE_DIR = Path(__file__).resolve().parent.parent.parent
ML_DIR = BASE_DIR / "ml"
ARTIFACTS_DIR = ML_DIR / "registry" / "artifacts"

@dataclass(frozen=True)
class MLConfig:
    RANDOM_SEED: int = 42
    TEST_SIZE: float = 0.2
    
    # Model Storage Paths
    ARTIFACTS_PATH: Path = ARTIFACTS_DIR
    REGISTRY_METADATA_FILE: Path = ARTIFACTS_DIR / "model_registry.json"
    
    # Customer Segmentation Parameters
    RFM_N_CLUSTERS: int = 4
    
    # Delivery Risk Hyperparameters
    DELIVERY_RISK_MODEL_TYPE: str = "HistGradientBoosting" # Fast, handles native interactions & missing values
    DELIVERY_MAX_ITER: int = 150
    DELIVERY_LEARNING_RATE: float = 0.08
    DELIVERY_MIN_SAMPLES_LEAF: int = 20
    
    # Satisfaction Risk Parameters
    SATISFACTION_MODEL_TYPE: str = "RandomForest"
    
    # Forecast Parameters
    FORECAST_HORIZON_DAYS: int = 30
    
    # Anomaly Parameters
    ANOMALY_Z_THRESHOLD: float = 2.5

    def ensure_directories(self):
        self.ARTIFACTS_PATH.mkdir(parents=True, exist_ok=True)

ml_config = MLConfig()
ml_config.ensure_directories()
