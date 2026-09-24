from sqlalchemy.orm import Session
from typing import List, Tuple, Optional
import math
from backend.app.repositories.customer_repository import CustomerRepository
from backend.app.schemas.customers import CustomerSegmentItem, CustomerSummaryItem, CustomerGeoItem
from backend.app.schemas.common import PaginationMetadata

class CustomerService:
    def __init__(self, db: Session):
        self.repo = CustomerRepository(db)

    def get_segments(self) -> List[CustomerSegmentItem]:
        rows = self.repo.get_segment_distribution()
        return [CustomerSegmentItem(**r) for r in rows]

    def get_geo_distribution(self) -> List[CustomerGeoItem]:
        rows = self.repo.get_geo_distribution()
        return [CustomerGeoItem(**r) for r in rows]

    def get_customers_paginated(
        self,
        page: int = 1,
        page_size: int = 20,
        segment: Optional[str] = None,
        state: Optional[str] = None
    ) -> Tuple[List[CustomerSummaryItem], PaginationMetadata]:
        rows, total = self.repo.get_customers_paginated(page=page, page_size=page_size, segment=segment, state=state)
        items = [CustomerSummaryItem(**r) for r in rows]
        meta = PaginationMetadata(
            page=page,
            page_size=page_size,
            total_records=total,
            total_pages=math.ceil(total / page_size) if total > 0 else 0
        )
        return items, meta
