"""Strict SQL Validator and Security Guardrails for OlistIQ AI Analyst."""

import re
import logging
from typing import Tuple, List, Set
from ai_analyst.config.ai_config import ai_config

logger = logging.getLogger("olistiq.ai_analyst.sql_validator")


class SQLValidator:
    """Enforces AST-like syntax checks, table allowlists, and execution safety."""

    @staticmethod
    def sanitize(sql: str) -> str:
        """Strips markdown code blocks, trailing semicolons, and comments."""
        cleaned = re.sub(r"```(?:sql)?\s*", "", sql, flags=re.IGNORECASE)
        cleaned = re.sub(r"\s*```", "", cleaned)
        # Remove single-line and multi-line comments
        cleaned = re.sub(r"--.*$", "", cleaned, flags=re.MULTILINE)
        cleaned = re.sub(r"/\*.*?\*/", "", cleaned, flags=re.DOTALL)
        cleaned = cleaned.strip()
        if cleaned.endswith(";"):
            cleaned = cleaned[:-1].strip()
        return cleaned

    @classmethod
    def validate(cls, raw_sql: str) -> Tuple[bool, str]:
        """Validates query against read-only constraints, table allowlists, and limits."""
        if not raw_sql or not raw_sql.strip():
            return False, "Generated SQL is empty."

        sql = cls.sanitize(raw_sql)

        # 1. Multiple Statement Check
        if ";" in sql:
            return False, "Multiple SQL statements are strictly forbidden."

        # 2. Read-Only Command Check (Must begin with SELECT or WITH)
        first_word = sql.split()[0].upper() if sql.split() else ""
        if first_word not in ["SELECT", "WITH"]:
            return False, f"Forbidden non-query operation '{first_word}'. Only SELECT queries are permitted."

        # 3. Forbidden SQL Commands / DDL / DML keywords
        sql_lower = sql.lower()
        for forbidden in ai_config.FORBIDDEN_SQL_COMMANDS:
            pattern = rf"\b{re.escape(forbidden)}\b"
            if re.search(pattern, sql_lower):
                return False, f"Forbidden SQL keyword or command detected: '{forbidden}'."

        # 4. Table Allowlist Verification
        # Extract table names from FROM and JOIN clauses
        table_matches = re.findall(r"\b(?:from|join)\s+([a-zA-Z0-9_]+)", sql_lower)
        for tbl in table_matches:
            if tbl not in ai_config.ALLOWED_TABLES:
                return False, f"Access to unauthorized table or view '{tbl}' is forbidden."

        # 5. LIMIT Protection Injection
        if not re.search(r"\blimit\s+\d+\b", sql_lower):
            sql = f"{sql}\nLIMIT {ai_config.DEFAULT_ROWS_LIMIT}"
        else:
            # Check that existing limit does not exceed MAX_ROWS_LIMIT
            limit_match = re.search(r"\blimit\s+(\d+)\b", sql_lower)
            if limit_match and int(limit_match.group(1)) > ai_config.MAX_ROWS_LIMIT:
                sql = re.sub(r"\blimit\s+\d+\b", f"LIMIT {ai_config.MAX_ROWS_LIMIT}", sql, flags=re.IGNORECASE)

        return True, sql


sql_validator = SQLValidator()
