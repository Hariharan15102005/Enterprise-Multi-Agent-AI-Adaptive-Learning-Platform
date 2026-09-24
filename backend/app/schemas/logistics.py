from typing import Optional, List
from pydantic import BaseModel

class LogisticsOverview(BaseModel):
    avg_delivery_days: float
    median_delivery_days: float
    on_time_delivery_rate: float
    late_delivery_rate: float
    avg_delay_days_for_late_orders: float
    avg_seller_dispatch_hours: float
    avg_carrier_transit_days: float
    interstate_orders_pct: float

class LogisticsByStateItem(BaseModel):
    state_code: str
    total_orders: int
    avg_delivery_days: float
    late_rate_pct: float
    avg_freight_brl: float
    avg_distance_km: float
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class LogisticsBySellerItem(BaseModel):
    seller_id: str
    seller_state: str
    total_shipments: int
    avg_dispatch_hours: float
    sla_breach_rate_pct: float
    avg_delivery_days: float
    seller_tier: str
