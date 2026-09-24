from sqlalchemy.orm import Session
from typing import List, Tuple, Optional
import math
from backend.app.repositories.product_repository import ProductRepository
from backend.app.schemas.products import ProductAnalyticsItem
from backend.app.schemas.common import PaginationMetadata

class ProductService:
    def __init__(self, db: Session):
        self.repo = ProductRepository(db)

    def get_products_paginated(
        self,
        page: int = 1,
        page_size: int = 20,
        category: Optional[str] = None,
        sort_by: str = "items_sold"
    ) -> Tuple[List[ProductAnalyticsItem], PaginationMetadata]:
        rows, total = self.repo.get_products_paginated(page=page, page_size=page_size, category=category, sort_by=sort_by)
        items = [ProductAnalyticsItem(**r) for r in rows]
        meta = PaginationMetadata(
            page=page,
            page_size=page_size,
            total_records=total,
            total_pages=math.ceil(total / page_size) if total > 0 else 0
        )
        return items, meta
