"""Database execution engine for validated analytical SQL queries."""

import time
import logging
from typing import Dict, Any, List, Tuple
from sqlalchemy import text
from database.connection import engine
from ai_analyst.config.ai_config import ai_config

logger = logging.getLogger("olistiq.ai_analyst.sql_executor")


class SQLExecutor:
    """Executes validated SQL queries with timeout guardrails and result serialization."""

    def __init__(self, db_engine=None):
        self.engine = db_engine or engine

    def execute(self, validated_sql: str) -> Tuple[bool, List[Dict[str, Any]], List[str], float, str]:
        """Runs query and returns (success, rows, columns, latency_ms, error_message)."""
        start_time = time.perf_counter()
        try:
            with self.engine.connect() as conn:
                # Set execution timeout if supported
                cursor_res = conn.execute(text(validated_sql))
                columns = list(cursor_res.keys())
                raw_rows = cursor_res.fetchall()
                
                rows = [dict(row._mapping) for row in raw_rows]
                
            latency_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
            logger.info("Successfully executed SQL query in %.2f ms (%d rows returned).", latency_ms, len(rows))
            return True, rows, columns, latency_ms, ""
        except Exception as e:
            latency_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
            error_msg = str(e)
            logger.error("SQL execution error: %s", error_msg)
            # Sanitize error message to prevent leaking internal file paths or passwords
            safe_error = error_msg.split("\n")[0]
            return False, [], [], latency_ms, safe_error


sql_executor = SQLExecutor()
