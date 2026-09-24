from typing import Optional, List
from pydantic import BaseModel

class RevenueTrendItem(BaseModel):
    period: str
    year: int
    month: Optional[int] = None
    gmv: float
    freight_value: float
    order_count: int
    aov: float
    avg_review_score: Optional[float] = None
    late_orders_count: int = 0

class CategoryAnalyticsItem(BaseModel):
    category_name_en: str
    total_orders: int
    total_items_sold: int
    total_gmv: float
    total_freight: float
    avg_price: float
    avg_review_score: Optional[float] = None
    late_rate_pct: float

class PaymentAnalyticsItem(BaseModel):
    payment_type: str
    total_transactions: int
    total_payment_value: float
    avg_payment_value: float
    avg_installments: float
    share_pct: float

class AnalyticalInsight(BaseModel):
    id: str
    type: str # 'GROWTH', 'LOGISTICS_RISK', 'CUSTOMER_OPPORTUNITY', 'MERCHANT_PERFORMANCE'
    title: str
    description: str
    severity: str # 'INFO', 'SUCCESS', 'WARNING', 'CRITICAL'
    metric_value: Optional[str] = None
    suggested_action: Optional[str] = None
