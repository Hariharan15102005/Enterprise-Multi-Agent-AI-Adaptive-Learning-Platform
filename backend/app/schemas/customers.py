from typing import Optional
from pydantic import BaseModel

class CustomerSegmentItem(BaseModel):
    segment_name: str
    customer_count: int
    share_pct: float
    total_spend_brl: float
    avg_recency_days: float
    avg_frequency: float
    avg_monetary_spend: float

class CustomerSummaryItem(BaseModel):
    customer_unique_id: str
    current_city: str
    current_state: str
    lifetime_order_count: int
    lifetime_spend_brl: float
    is_repeat_customer: bool
    rfm_recency_days: Optional[int] = None
    rfm_frequency_score: Optional[int] = None
    rfm_monetary_score: Optional[int] = None
    rfm_segment: Optional[str] = None

class CustomerGeoItem(BaseModel):
    state_code: str
    state_name: Optional[str] = None
    region: Optional[str] = None
    customer_count: int
    percentage_of_total: Optional[float] = None
    rank: Optional[int] = None
    total_spend_brl: float
    avg_spend_per_customer: float
    total_orders: Optional[int] = None
    avg_review_score: Optional[float] = None
    repeat_customer_rate: float
    latitude: Optional[float] = None
    longitude: Optional[float] = None
