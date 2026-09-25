"""LangGraph nodes for the OlistIQ AI Analyst workflow."""

import time
import uuid
import logging
from typing import Dict, Any

from ai_analyst.state.agent_state import AgentState, AgentIntent, ResponseType
from ai_analyst.security.guardrails import security_guardrails
from ai_analyst.routing.hybrid_router import hybrid_router
from ai_analyst.schema_retriever.schema_store import schema_store
from ai_analyst.metrics.metric_catalog import metric_catalog
from ai_analyst.planning.query_planner import query_planner
from ai_analyst.sql.generator import sql_generator
from ai_analyst.sql.validator import sql_validator
from ai_analyst.sql.executor import sql_executor
from ai_analyst.insights.synthesizer import insight_synthesizer
from ai_analyst.config.ai_config import ai_config

logger = logging.getLogger("olistiq.ai_analyst.nodes")


def check_security_node(state: AgentState) -> Dict[str, Any]:
    """Inspects question for prompt injection and administrative attack patterns."""
    question = state.get("question", "")
    is_safe, reason = security_guardrails.inspect_input(question)
    
    if not is_safe:
        return {
            "intent": AgentIntent.SECURITY_REJECTED.value,
            "final_answer": reason,
            "response_type": ResponseType.ERROR.value,
            "error": "Security check failed",
            "warnings": ["Adversarial query rejected by security guardrails."]
        }
    return {"warnings": []}


def classify_intent_node(state: AgentState) -> Dict[str, Any]:
    """Classifies query intent and determines if ML or SQL path is appropriate."""
    question = state.get("question", "")
    
    # Check ML routing first
    is_ml, ml_intent, route_params = hybrid_router.identify_ml_intent(question)
    if is_ml:
        return {
            "is_ml_route": True,
            "intent": ml_intent,
            "entities": route_params or {}
        }

    q_lower = question.lower()
    intent = AgentIntent.KPI_LOOKUP.value

    if any(w in q_lower for w in ["month", "monthly", "trend", "daily", "timeline", "over time", "history"]):
        intent = AgentIntent.TIME_SERIES.value
    elif any(w in q_lower for w in ["top", "highest", "best", "leader", "ranking", "most", "lowest"]):
        intent = AgentIntent.RANKING.value
    elif any(w in q_lower for w in ["compare", "versus", "vs", "difference"]):
        intent = AgentIntent.COMPARISON.value
    elif any(w in q_lower for w in ["seller", "merchant"]):
        intent = AgentIntent.SELLER_ANALYTICS.value
    elif any(w in q_lower for w in ["category", "product"]):
        intent = AgentIntent.CATEGORY_ANALYTICS.value
    elif any(w in q_lower for w in ["customer", "repeat", "buyer"]):
        intent = AgentIntent.CUSTOMER_ANALYTICS.value
    elif any(w in q_lower for w in ["late", "delay", "delivery", "logistics", "freight"]):
        intent = AgentIntent.LOGISTICS_ANALYTICS.value
    elif any(w in q_lower for w in ["payment", "installments"]):
        intent = AgentIntent.PAYMENT_ANALYTICS.value
    elif any(w in q_lower for w in ["review", "rating", "score"]):
        intent = AgentIntent.REVIEW_ANALYTICS.value
    elif any(w in q_lower for w in ["state", "region", "city", "geo"]):
        intent = AgentIntent.GEOGRAPHY_ANALYTICS.value

    return {
        "is_ml_route": False,
        "intent": intent,
        "entities": {}
    }


def route_ml_node(state: AgentState) -> Dict[str, Any]:
    """Executes predictive intelligence models for forecasting, anomalies, segments, or risk."""
    intent = state.get("intent", AgentIntent.FORECASTING.value)
    entities = state.get("entities", {})
    ml_res = hybrid_router.execute_ml_route(intent, entities)
    
    return {
        "final_answer": ml_res.get("answer", ""),
        "query_result": ml_res.get("data", []),
        "columns": ml_res.get("columns", []),
        "response_type": ml_res.get("response_type", ResponseType.TEXT.value),
        "visualization": ml_res.get("visualization", {}),
        "model_version": ml_res.get("model_version", "v1.0")
    }


def retrieve_schema_and_metrics_node(state: AgentState) -> Dict[str, Any]:
    """Retrieves relevant schema context and metric formulas."""
    question = state.get("question", "")
    intent = state.get("intent", AgentIntent.KPI_LOOKUP.value)
    
    schema_ctx = schema_store.get_relevant_schema(intent, question)
    metric_ctx = metric_catalog.get_relevant_metrics(question)
    
    return {
        "schema_context": schema_ctx,
        "metric_context": metric_ctx
    }


def create_query_plan_node(state: AgentState) -> Dict[str, Any]:
    """Generates structured query plan with conversation context."""
    question = state.get("question", "")
    intent = state.get("intent", AgentIntent.KPI_LOOKUP.value)
    context = state.get("conversation_context") or []
    
    plan = query_planner.plan(question, intent, conversation_context=context)
    return {"query_plan": plan}


def generate_sql_node(state: AgentState) -> Dict[str, Any]:
    """Translates question and plan into analytical SQL."""
    question = state.get("question", "")
    plan = state.get("query_plan", {})
    schema_ctx = state.get("schema_context", "")
    metric_ctx = state.get("metric_context", "")
    
    raw_sql = sql_generator.generate(question, plan, schema_ctx, metric_ctx)
    return {"generated_sql": raw_sql}


def validate_sql_node(state: AgentState) -> Dict[str, Any]:
    """Applies strict security and syntactic validation to generated SQL."""
    raw_sql = state.get("generated_sql", "")
    is_valid, validated_or_err = sql_validator.validate(raw_sql)
    
    if not is_valid:
        logger.warning("SQL validation failed: %s", validated_or_err)
        return {
            "validated_sql": None,
            "error": f"Validation Error: {validated_or_err}"
        }
    return {
        "validated_sql": validated_or_err,
        "error": None
    }


def execute_sql_node(state: AgentState) -> Dict[str, Any]:
    """Executes validated SQL against analytical database."""
    val_sql = state.get("validated_sql", "")
    if not val_sql:
        return {"error": "No validated SQL available for execution."}
        
    success, rows, columns, latency_ms, err = sql_executor.execute(val_sql)
    
    if not success:
        return {
            "query_result": None,
            "columns": None,
            "error": err or "Database execution failed",
            "execution_time_ms": latency_ms
        }
        
    return {
        "query_result": rows,
        "columns": columns,
        "error": None,
        "execution_time_ms": latency_ms
    }


def repair_sql_node(state: AgentState) -> Dict[str, Any]:
    """Attempts controlled SQL regeneration if execution or validation failed."""
    current_retry = state.get("retry_count", 0) + 1
    logger.info("Triggering SQL Repair loop (Retry %d / %d)...", current_retry, ai_config.MAX_SQL_RETRIES)
    
    plan = state.get("query_plan", {})
    question = state.get("question", "")
    
    # Fallback to robust deterministic template
    fallback_sql = sql_generator.generate_sql_from_plan(plan, question)
    
    return {
        "generated_sql": fallback_sql,
        "retry_count": current_retry,
        "error": None,
        "warnings": [f"SQL query required repair cycle (retry {current_retry})."]
    }


def generate_insights_node(state: AgentState) -> Dict[str, Any]:
    """Synthesizes factual natural language answer and UI visualization."""
    question = state.get("question", "")
    rows = state.get("query_result") or []
    columns = state.get("columns") or []
    plan = state.get("query_plan")
    
    answer, insights, viz, resp_type, followups, caveats = insight_synthesizer.synthesize(question, rows, columns, plan)
    
    return {
        "final_answer": answer,
        "insights": insights,
        "visualization": viz,
        "response_type": resp_type,
        "suggested_followups": followups,
        "caveats": caveats
    }


def format_response_node(state: AgentState) -> Dict[str, Any]:
    """Finalizes response metadata and error handling."""
    if state.get("error") and not state.get("final_answer"):
        return {
            "final_answer": f"Unable to complete analytical query: {state.get('error')}",
            "response_type": ResponseType.ERROR.value,
            "suggested_followups": ["What is our total revenue?", "Show monthly sales trends.", "What are the top 5 product categories?"]
        }
    return {}
