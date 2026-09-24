"""FastAPI endpoints for the OlistIQ AI Analyst."""

import logging
from fastapi import APIRouter, HTTPException, Body
from backend.app.schemas.ai import AIQueryRequest, AIQueryResponse, AICapabilitiesResponse
from ai_analyst.service import ai_service
from ai_analyst.config.ai_config import ai_config
from ai_analyst.state.agent_state import AgentIntent, ResponseType

logger = logging.getLogger("olistiq.api.ai")
router = APIRouter(prefix="/ai", tags=["AI Analyst / Natural Language to SQL"])


@router.post("/query", response_model=AIQueryResponse)
def query_ai_analyst(payload: AIQueryRequest = Body(...)):
    """Processes natural language business questions via the LangGraph state machine."""
    try:
        response_dict = ai_service.process_query(
            question=payload.question,
            conversation_context=payload.conversation_context
        )
        return response_dict
    except Exception as e:
        logger.error("AI Analyst endpoint unexpected failure: %s", str(e), exc_info=True)
        raise HTTPException(status_code=500, detail="An error occurred while processing the analytical question.")


@router.get("/health")
def get_ai_analyst_health():
    """Returns operational health of the AI Analyst and LangGraph engine."""
    return {
        "status": "healthy",
        "service": "OlistIQ AI Analyst",
        "langgraph_workflow": "compiled_and_active",
        "guardrails": "enforced"
    }


@router.get("/capabilities", response_model=AICapabilitiesResponse)
def get_ai_analyst_capabilities():
    """Returns supported intents, response types, allowed tables, and guardrail settings."""
    return {
        "status": "active",
        "engine": "LangGraph + PostgreSQL/SQLite NL2SQL + ML Hybrid Router",
        "langgraph_workflow": "StateGraph(check_security -> classify_intent -> plan -> sql_gen -> validate -> execute -> synthesize)",
        "supported_intents": [i.value for i in AgentIntent],
        "supported_response_types": [r.value for r in ResponseType],
        "allowed_tables": sorted(list(ai_config.ALLOWED_TABLES)),
        "guardrails_enabled": True
    }
