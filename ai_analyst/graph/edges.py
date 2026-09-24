"""Conditional edges and routing logic for the OlistIQ LangGraph AI Analyst."""

from typing import Literal
from ai_analyst.state.agent_state import AgentState, AgentIntent
from ai_analyst.config.ai_config import ai_config


def check_security_edge(state: AgentState) -> Literal["format_response", "classify_intent"]:
    """Routes to rejection exit if adversarial prompt pattern was detected."""
    if state.get("intent") == AgentIntent.SECURITY_REJECTED.value:
        return "format_response"
    return "classify_intent"


def route_intent_edge(state: AgentState) -> Literal["route_ml", "retrieve_schema_and_metrics"]:
    """Directs execution to either Phase 5 ML Inference services or SQL Analytics engine."""
    if state.get("is_ml_route", False):
        return "route_ml"
    return "retrieve_schema_and_metrics"


def validate_sql_edge(state: AgentState) -> Literal["execute_sql", "repair_sql", "format_response"]:
    """Decides whether to execute query, trigger repair cycle, or abort with validation error."""
    if state.get("error"):
        if state.get("retry_count", 0) < ai_config.MAX_SQL_RETRIES:
            return "repair_sql"
        return "format_response"
    return "execute_sql"


def execute_sql_edge(state: AgentState) -> Literal["generate_insights", "repair_sql", "format_response"]:
    """Decides whether to synthesize insights, trigger repair, or abort upon database execution error."""
    if state.get("error"):
        if state.get("retry_count", 0) < ai_config.MAX_SQL_RETRIES:
            return "repair_sql"
        return "format_response"
    return "generate_insights"
