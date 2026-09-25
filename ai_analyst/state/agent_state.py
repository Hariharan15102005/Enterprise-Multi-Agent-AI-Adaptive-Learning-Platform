"""State definitions and typed schemas for the OlistIQ LangGraph AI Analyst."""

from enum import Enum
from typing import TypedDict, Optional, List, Dict, Any
from pydantic import BaseModel, Field


class AgentIntent(str, Enum):
    KPI_LOOKUP = "KPI_LOOKUP"
    TIME_SERIES = "TIME_SERIES"
    RANKING = "RANKING"
    COMPARISON = "COMPARISON"
    PROPORTION_SHARE = "PROPORTION_SHARE"
    CORRELATION = "CORRELATION"
    DISTRIBUTION = "DISTRIBUTION"
    CUSTOMER_ANALYTICS = "CUSTOMER_ANALYTICS"
    CUSTOMER_SEGMENTATION = "CUSTOMER_SEGMENTATION"
    PRODUCT_ANALYTICS = "PRODUCT_ANALYTICS"
    CATEGORY_ANALYTICS = "CATEGORY_ANALYTICS"
    SELLER_ANALYTICS = "SELLER_ANALYTICS"
    LOGISTICS_ANALYTICS = "LOGISTICS_ANALYTICS"
    PAYMENT_ANALYTICS = "PAYMENT_ANALYTICS"
    REVIEW_ANALYTICS = "REVIEW_ANALYTICS"
    GEOGRAPHY_ANALYTICS = "GEOGRAPHY_ANALYTICS"
    ANOMALY_ANALYSIS = "ANOMALY_ANALYSIS"
    FORECASTING = "FORECASTING"
    ML_PREDICTION = "ML_PREDICTION"
    SECURITY_REJECTED = "SECURITY_REJECTED"
    UNSUPPORTED = "UNSUPPORTED"


class ChartType(str, Enum):
    KPI = "kpi"
    BAR = "bar"
    HORIZONTAL_BAR = "horizontal_bar"
    LINE = "line"
    AREA = "area"
    DONUT = "donut"
    PIE = "pie"
    SCATTER = "scatter"
    HISTOGRAM = "histogram"
    TABLE = "table"


class ResponseType(str, Enum):
    KPI = "KPI"
    TABLE = "TABLE"
    TIME_SERIES = "TIME_SERIES"
    RANKING = "RANKING"
    COMPARISON = "COMPARISON"
    CORRELATION = "CORRELATION"
    DISTRIBUTION = "DISTRIBUTION"
    PREDICTION = "PREDICTION"
    FORECAST = "FORECAST"
    ANOMALY = "ANOMALY"
    TEXT = "TEXT"
    ERROR = "ERROR"
    UNSUPPORTED = "UNSUPPORTED"


class VisualizationMeta(BaseModel):
    recommended_chart: str = "table"  # kpi, bar, horizontal_bar, line, area, donut, pie, scatter, histogram, table
    chart_type: str = "table"
    title: Optional[str] = None
    description: Optional[str] = None
    x_key: Optional[str] = None
    y_key: Optional[str] = None
    z_key: Optional[str] = None
    x_axis_label: Optional[str] = None
    y_axis_label: Optional[str] = None
    value_format: str = "number"  # currency, percentage, number, duration
    kpi_value: Optional[str] = None
    kpi_unit: Optional[str] = None
    kpi_subtitle: Optional[str] = None
    chart_config: Dict[str, Any] = Field(default_factory=dict)
    data: Optional[List[Dict[str, Any]]] = None


class QueryPlan(BaseModel):
    metric: str
    dimension: Optional[str] = None
    secondary_dimension: Optional[str] = None
    filters: Dict[str, Any] = Field(default_factory=dict)
    aggregation: str = "SUM"
    group_by: Optional[List[str]] = None
    order_by: Optional[str] = None
    order_direction: str = "DESC"
    limit: int = 20
    target_table_or_view: str = "analytics_obt_orders"
    intent: str = "KPI_LOOKUP"
    chart_hint: Optional[str] = None


class AgentState(TypedDict, total=False):
    request_id: str
    question: str
    conversation_context: List[Dict[str, str]]
    intent: str
    entities: Dict[str, Any]
    filters: Dict[str, Any]
    schema_context: str
    metric_context: str
    query_plan: Optional[Dict[str, Any]]
    generated_sql: Optional[str]
    validated_sql: Optional[str]
    query_result: Optional[List[Dict[str, Any]]]
    columns: Optional[List[str]]
    result_metadata: Dict[str, Any]
    insights: List[str]
    warnings: List[str]
    caveats: Optional[str]
    suggested_followups: List[str]
    error: Optional[str]
    retry_count: int
    response_type: str
    visualization: Optional[Dict[str, Any]]
    final_answer: str
    execution_time_ms: float
    model_version: str
    is_ml_route: bool
    ml_output: Optional[Dict[str, Any]]
