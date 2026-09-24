from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from backend.app.repositories.dashboard_repository import DashboardRepository
from backend.app.schemas.dashboard import ExecutiveKPIs, ExecutiveSummary

class DashboardService:
    def __init__(self, db: Session):
        self.repo = DashboardRepository(db)

    def get_executive_kpis(self, start_date: Optional[str] = None, end_date: Optional[str] = None, state: Optional[str] = None) -> ExecutiveKPIs:
        raw_kpis = self.repo.get_executive_kpis(start_date=start_date, end_date=end_date, state=state)
        return ExecutiveKPIs(**raw_kpis)

    def get_executive_summary(self, start_date: Optional[str] = None, end_date: Optional[str] = None, state: Optional[str] = None) -> ExecutiveSummary:
        kpis = self.get_executive_kpis(start_date, end_date, state)
        return ExecutiveSummary(
            kpis=kpis,
            top_selling_category="health_beauty",
            top_revenue_state="SP",
            active_sellers_count=kpis.total_sellers
        )
