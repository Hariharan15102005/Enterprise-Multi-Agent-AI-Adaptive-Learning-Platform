"""Master service orchestrator for the OlistIQ AI Analyst."""

import time
import uuid
import logging
from typing import Dict, Any, List, Optional

from ai_analyst.graph.workflow import ai_analyst_graph
from ai_analyst.state.agent_state import AgentState, ResponseType

logger = logging.getLogger("olistiq.ai_analyst.service")


class AIAnalystService:
    """Provides high-level API to process natural language questions via LangGraph."""

    def __init__(self):
        self.graph = ai_analyst_graph

    def process_query(
        self,
        question: str,
        conversation_context: Optional[List[Dict[str, str]]] = None,
        request_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Executes full LangGraph pipeline on user question and returns frontend-friendly result."""
        req_id = request_id or f"ai_req_{uuid.uuid4().hex[:12]}"
        start_time = time.perf_counter()
        
        logger.info("Processing AI Analyst Query [%s]: '%s'", req_id, question)

        initial_state: AgentState = {
            "request_id": req_id,
            "question": question,
            "conversation_context": conversation_context or [],
            "intent": "UNKNOWN",
            "entities": {},
            "filters": {},
            "schema_context": "",
            "metric_context": "",
            "query_plan": None,
            "generated_sql": None,
            "validated_sql": None,
            "query_result": None,
            "columns": [],
            "result_metadata": {},
            "insights": [],
            "warnings": [],
            "error": None,
            "retry_count": 0,
            "response_type": ResponseType.TEXT.value,
            "visualization": {},
            "final_answer": "",
            "execution_time_ms": 0.0,
            "model_version": "v1.0",
            "is_ml_route": False,
            "ml_output": None
        }

        # Run compiled LangGraph workflow
        final_state = self.graph.invoke(initial_state)

        total_latency_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
        logger.info("AI Analyst Query [%s] completed in %.2f ms (Intent: %s)", req_id, total_latency_ms, final_state.get("intent"))

        return {
            "request_id": req_id,
            "question": question,
            "intent": final_state.get("intent", "UNKNOWN"),
            "response_type": final_state.get("response_type", ResponseType.TEXT.value),
            "answer": final_state.get("final_answer", ""),
            "data": final_state.get("query_result") or [],
            "columns": final_state.get("columns") or [],
            "sql": final_state.get("validated_sql"),
            "visualization": final_state.get("visualization") or {"recommended_chart": "table", "chart_type": "table"},
            "insights": final_state.get("insights") or [],
            "suggested_followups": final_state.get("suggested_followups") or [],
            "caveats": final_state.get("caveats"),
            "warnings": final_state.get("warnings") or [],
            "error": final_state.get("error"),
            "execution_time_ms": total_latency_ms,
            "model_version": final_state.get("model_version", "v1.0")
        }


ai_service = AIAnalystService()
