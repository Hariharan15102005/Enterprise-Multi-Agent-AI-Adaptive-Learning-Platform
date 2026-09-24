from typing import Optional
from pydantic import BaseModel

class ProductAnalyticsItem(BaseModel):
    product_id: str
    category_name_en: str
    items_sold: int
    total_gmv_brl: float
    avg_price_brl: float
    avg_freight_brl: float
    weight_g: float
    volume_cm3: float
    size_tier: str
    avg_review_score: Optional[float] = None
