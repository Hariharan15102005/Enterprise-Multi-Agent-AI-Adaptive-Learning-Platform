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
    category: Optional[str] = None
    total_orders: int
    orders: Optional[int] = None
    total_items_sold: int
    items_sold: Optional[int] = None
    total_gmv: float
    gmv: Optional[float] = None
    total_freight: float
    avg_price: float
    contribution_pct: Optional[float] = None
    avg_review_score: Optional[float] = None
    late_rate_pct: float
    late_rate: Optional[float] = None

class PaymentAnalyticsItem(BaseModel):
    payment_type: str
    payment_channel: Optional[str] = None
    total_transactions: int
    transaction_count: Optional[int] = None
    total_payment_value: float
    total_value: Optional[float] = None
    avg_payment_value: float
    avg_installments: float
    share_pct: float
    val_share_pct: Optional[float] = None
    tx_share_pct: Optional[float] = None

class AnalyticalInsight(BaseModel):
    id: str
    type: str # 'GROWTH', 'LOGISTICS_RISK', 'CUSTOMER_OPPORTUNITY', 'MERCHANT_PERFORMANCE'
    title: str
    description: str
    severity: str # 'INFO', 'SUCCESS', 'WARNING', 'CRITICAL'
    metric_value: Optional[str] = None
    suggested_action: Optional[str] = None
