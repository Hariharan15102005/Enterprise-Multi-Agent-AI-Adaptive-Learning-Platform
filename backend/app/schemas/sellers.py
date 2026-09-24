from typing import Optional
from pydantic import BaseModel

class SellerAnalyticsItem(BaseModel):
    seller_id: str
    seller_city: str
    seller_state: str
    seller_tier: str
    orders_fulfilled: int
    total_sales_value_brl: float
    avg_order_value_brl: float
    avg_dispatch_time_hours: Optional[float] = None
    sla_breach_rate_pct: Optional[float] = None
    avg_review_score: Optional[float] = None
