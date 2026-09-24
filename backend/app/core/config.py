"""Centralized backend configuration settings."""

import os
from pydantic import BaseModel
from config.settings import settings as base_settings


class BackendConfig(BaseModel):
    APP_NAME: str = "OlistIQ Decision Intelligence API"
    APP_VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"
    ENVIRONMENT: str = base_settings.ENVIRONMENT
    LOG_LEVEL: str = base_settings.LOG_LEVEL
    DATABASE_URL: str = base_settings.DATABASE_URL
    
    # Standardized CORS origins for Vite, React, and local environments
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://localhost:8080",
        "http://localhost:8000"
    ]


backend_config = BackendConfig()
