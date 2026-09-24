from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from backend.app.db.session import get_db
from backend.app.services.analytics_service import AnalyticsService
from backend.app.schemas.common import StandardResponse
from backend.app.schemas.analytics import RevenueTrendItem, CategoryAnalyticsItem, PaymentAnalyticsItem, AnalyticalInsight

router = APIRouter(prefix="/analytics", tags=["Business Analytics"])

@router.get("/revenue", response_model=StandardResponse[List[RevenueTrendItem]])
def get_revenue_trends(
    interval: str = Query("month", pattern="^(day|month)$", description="Aggregation granularity (day or month)"),
    start_date: Optional[str] = Query(None, description="ISO Start Date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="ISO End Date (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    service = AnalyticsService(db)
    trends = service.get_revenue_trends(interval=interval, start_date=start_date, end_date=end_date)
    return StandardResponse(data=trends)

@router.get("/categories", response_model=StandardResponse[List[CategoryAnalyticsItem]])
def get_category_analytics(
    limit: int = Query(20, ge=1, le=100),
    sort_by: str = Query("gmv", pattern="^(gmv|orders|late_rate)$"),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    service = AnalyticsService(db)
    categories = service.get_category_analytics(limit=limit, sort_by=sort_by, start_date=start_date, end_date=end_date)
    return StandardResponse(data=categories)

@router.get("/payments", response_model=StandardResponse[List[PaymentAnalyticsItem]])
def get_payment_analytics(db: Session = Depends(get_db)):
    service = AnalyticsService(db)
    payments = service.get_payment_analytics()
    return StandardResponse(data=payments)

@router.get("/insights", response_model=StandardResponse[List[AnalyticalInsight]])
def get_insights(db: Session = Depends(get_db)):
    service = AnalyticsService(db)
    insights = service.get_insights()
    return StandardResponse(data=insights)
