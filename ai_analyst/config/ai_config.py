"""Configuration settings for the OlistIQ AI Analyst and LangGraph engine."""

import os
from dataclasses import dataclass
from typing import Set

@dataclass(frozen=True)
class AIConfig:
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "gemini")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gemini-1.5-pro")
    TEMPERATURE: float = float(os.getenv("AI_TEMPERATURE", "0.0"))
    
    # Query Execution Guardrails
    QUERY_TIMEOUT_SECONDS: int = int(os.getenv("AI_QUERY_TIMEOUT", "10"))
    MAX_SQL_RETRIES: int = int(os.getenv("AI_MAX_SQL_RETRIES", "2"))
    MAX_ROWS_LIMIT: int = int(os.getenv("AI_MAX_ROWS_LIMIT", "100"))
    DEFAULT_ROWS_LIMIT: int = int(os.getenv("AI_DEFAULT_ROWS_LIMIT", "20"))
    
    # Allowed Analytical Tables & Views
    ALLOWED_TABLES: Set[str] = frozenset({
        "dim_customer",
        "dim_seller",
        "dim_product",
        "dim_geolocation",
        "dim_date",
        "fact_orders",
        "fact_order_items",
        "fact_payments",
        "fact_reviews",
        "analytics_obt_orders",
        "agg_daily_sales_ops",
        "agg_monthly_category_perf"
    })
    
    # Prohibited SQL Keywords / Commands
    FORBIDDEN_SQL_COMMANDS: Set[str] = frozenset({
        "insert", "update", "delete", "drop", "alter", "truncate",
        "create", "grant", "revoke", "copy", "call", "vacuum",
        "attach", "detach", "reindex", "pragma", "commit", "rollback",
        "execute", "exec", "declare", "merge", "replace", "system"
    })

ai_config = AIConfig()
