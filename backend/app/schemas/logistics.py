from typing import Optional, List
from pydantic import BaseModel

class LogisticsOverview(BaseModel):
    avg_delivery_days: float
    avg_delivery_time_days: Optional[float] = None
    median_delivery_days: float
    on_time_delivery_rate: float
    late_delivery_rate: float
    delayed_orders: Optional[int] = 0
    avg_freight_value: Optional[float] = 0.0
    avg_delay_days_for_late_orders: float
    avg_seller_dispatch_hours: float
    avg_carrier_transit_days: float
    interstate_orders_pct: float

class LogisticsByStateItem(BaseModel):
    state_code: str
    state_name: str
    state: Optional[str] = None
    delivered_volume: int
    total_orders: int
    avg_delivery_days: Optional[float] = None
    avg_delivery_time_days: Optional[float] = None
    average_transit_days: Optional[float] = None
    avg_transit_days: Optional[float] = None
    on_time_rate: Optional[float] = None
    late_rate_pct: Optional[float] = None
    avg_freight_cost: Optional[float] = None
    avg_freight_brl: Optional[float] = None
    avg_distance_km: Optional[float] = 650.0
    logistics_status: str
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
