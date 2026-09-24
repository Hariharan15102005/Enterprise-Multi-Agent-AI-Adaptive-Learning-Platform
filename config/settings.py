import os
from pathlib import Path
from dataclasses import dataclass

BASE_DIR = Path(__file__).resolve().parent.parent

@dataclass(frozen=True)
class Settings:
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Raw Data Path (Immutable Source)
    RAW_DATA_PATH: Path = BASE_DIR / os.getenv("RAW_DATA_PATH", "archive")
    
    # Processed Data Paths
    PROCESSED_DATA_PATH: Path = BASE_DIR / os.getenv("PROCESSED_DATA_PATH", "data/processed")
    QUARANTINE_DATA_PATH: Path = BASE_DIR / os.getenv("QUARANTINE_DATA_PATH", "data/quarantine")
    
    # Database Settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR}/data/processed/olistiq.db")
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT: int = int(os.getenv("POSTGRES_PORT", "5432"))
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "olistiq")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "")
    
    # Pipeline Settings
    BATCH_SIZE: int = int(os.getenv("BATCH_SIZE", "10000"))
    IDEMPOTENT_MODE: str = os.getenv("IDEMPOTENT_MODE", "REPLACE_ALL")

    def ensure_directories(self):
        self.PROCESSED_DATA_PATH.mkdir(parents=True, exist_ok=True)
        self.QUARANTINE_DATA_PATH.mkdir(parents=True, exist_ok=True)

settings = Settings()
settings.ensure_directories()
