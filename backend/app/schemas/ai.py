"""Pydantic request and response schemas for OlistIQ AI Analyst REST endpoints."""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class AIQueryRequest(BaseModel):
    question: str = Field(..., min_length=2, max_length=1000, json_schema_extra={"example": "What was the total GMV in 2018?"})
    conversation_context: Optional[List[Dict[str, str]]] = Field(default=None, json_schema_extra={"example": []})


class VisualizationSchema(BaseModel):
    recommended_chart: str = Field(default="table", json_schema_extra={"example": "line"})
    x_field: Optional[str] = Field(default=None, json_schema_extra={"example": "purchase_month"})
    y_field: Optional[str] = Field(default=None, json_schema_extra={"example": "total_gmv_brl"})
    title: Optional[str] = Field(default=None, json_schema_extra={"example": "Monthly GMV Trend"})
    chart_config: Dict[str, Any] = Field(default_factory=dict)


class AIQueryResponse(BaseModel):
    request_id: str
    question: str
    intent: str
    response_type: str
    answer: str
    data: List[Dict[str, Any]] = Field(default_factory=list)
    columns: List[str] = Field(default_factory=list)
    sql: Optional[str] = None
    visualization: Dict[str, Any] = Field(default_factory=dict)
    insights: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    error: Optional[str] = None
    execution_time_ms: float
    model_version: str


class AICapabilitiesResponse(BaseModel):
    status: str
    engine: str
    langgraph_workflow: str
    supported_intents: List[str]
    supported_response_types: List[str]
    allowed_tables: List[str]
    guardrails_enabled: bool
