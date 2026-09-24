from typing import Optional
from pydantic import BaseModel

class ExecutiveKPIs(BaseModel):
    gross_merchandise_value: float
    total_orders: int
    total_customers: int
    total_sellers: int
    total_products: int
    average_order_value: float
    average_review_score: float
    on_time_delivery_rate: float
    late_delivery_rate: float
    repeat_customer_rate: float
    total_freight_value: float

class ExecutiveSummary(BaseModel):
    kpis: ExecutiveKPIs
    top_selling_category: Optional[str] = None
    top_revenue_state: Optional[str] = None
    active_sellers_count: int = 0
