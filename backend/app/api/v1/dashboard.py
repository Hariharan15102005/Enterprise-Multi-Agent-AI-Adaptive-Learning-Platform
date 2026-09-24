from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from backend.app.db.session import get_db
from backend.app.services.dashboard_service import DashboardService
from backend.app.schemas.common import StandardResponse
from backend.app.schemas.dashboard import ExecutiveKPIs, ExecutiveSummary

router = APIRouter(prefix="/dashboard", tags=["Executive Dashboard"])

@router.get("/kpis", response_model=StandardResponse[ExecutiveKPIs])
def get_executive_kpis(
    start_date: Optional[str] = Query(None, description="ISO Start Date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="ISO End Date (YYYY-MM-DD)"),
    state: Optional[str] = Query(None, description="2-letter Brazilian State Code (e.g. SP, RJ)"),
    db: Session = Depends(get_db)
):
    service = DashboardService(db)
    kpis = service.get_executive_kpis(start_date=start_date, end_date=end_date, state=state)
    return StandardResponse(data=kpis)

@router.get("/summary", response_model=StandardResponse[ExecutiveSummary])
def get_executive_summary(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    state: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    service = DashboardService(db)
    summary = service.get_executive_summary(start_date=start_date, end_date=end_date, state=state)
    return StandardResponse(data=summary)
