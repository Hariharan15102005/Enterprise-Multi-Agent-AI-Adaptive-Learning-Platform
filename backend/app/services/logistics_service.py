from sqlalchemy.orm import Session
from typing import List, Dict, Any
from backend.app.repositories.logistics_repository import LogisticsRepository
from backend.app.schemas.logistics import LogisticsOverview, LogisticsByStateItem, LogisticsBySellerItem

class LogisticsService:
    def __init__(self, db: Session):
        self.repo = LogisticsRepository(db)

    def get_overview(self) -> LogisticsOverview:
        data = self.repo.get_logistics_overview()
        return LogisticsOverview(**data)

    def get_by_state(self) -> List[LogisticsByStateItem]:
        rows = self.repo.get_logistics_by_state()
        return [LogisticsByStateItem(**r) for r in rows]

    def get_by_seller(self, limit: int = 20) -> List[LogisticsBySellerItem]:
        rows = self.repo.get_logistics_by_seller(limit=limit)
        return [LogisticsBySellerItem(**r) for r in rows]
