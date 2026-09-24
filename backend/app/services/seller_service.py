from sqlalchemy.orm import Session
from typing import List, Tuple, Optional
import math
from backend.app.repositories.seller_repository import SellerRepository
from backend.app.schemas.sellers import SellerAnalyticsItem
from backend.app.schemas.common import PaginationMetadata

class SellerService:
    def __init__(self, db: Session):
        self.repo = SellerRepository(db)

    def get_sellers_paginated(
        self,
        page: int = 1,
        page_size: int = 20,
        tier: Optional[str] = None,
        state: Optional[str] = None
    ) -> Tuple[List[SellerAnalyticsItem], PaginationMetadata]:
        rows, total = self.repo.get_sellers_paginated(page=page, page_size=page_size, tier=tier, state=state)
        items = [SellerAnalyticsItem(**r) for r in rows]
        meta = PaginationMetadata(
            page=page,
            page_size=page_size,
            total_records=total,
            total_pages=math.ceil(total / page_size) if total > 0 else 0
        )
        return items, meta
