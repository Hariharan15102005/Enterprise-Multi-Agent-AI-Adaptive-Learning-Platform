from sqlalchemy.orm import Session
from typing import List, Optional
from backend.app.repositories.analytics_repository import AnalyticsRepository
from backend.app.schemas.analytics import RevenueTrendItem, CategoryAnalyticsItem, PaymentAnalyticsItem, AnalyticalInsight

class AnalyticsService:
    def __init__(self, db: Session):
        self.repo = AnalyticsRepository(db)

    def get_revenue_trends(self, interval: str = "month", start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[RevenueTrendItem]:
        rows = self.repo.get_revenue_trends(interval=interval, start_date=start_date, end_date=end_date)
        return [RevenueTrendItem(**r) for r in rows]

    def get_category_analytics(self, limit: int = 20, sort_by: str = "gmv", start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[CategoryAnalyticsItem]:
        rows = self.repo.get_category_analytics(limit=limit, sort_by=sort_by, start_date=start_date, end_date=end_date)
        return [CategoryAnalyticsItem(**r) for r in rows]

    def get_payment_analytics(self) -> List[PaymentAnalyticsItem]:
        rows = self.repo.get_payment_analytics()
        return [PaymentAnalyticsItem(**r) for r in rows]

    def get_insights(self) -> List[AnalyticalInsight]:
        rows = self.repo.get_insights()
        return [AnalyticalInsight(**r) for r in rows]
