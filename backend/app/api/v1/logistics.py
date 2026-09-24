from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List
from backend.app.db.session import get_db
from backend.app.services.logistics_service import LogisticsService
from backend.app.schemas.common import StandardResponse
from backend.app.schemas.logistics import LogisticsOverview, LogisticsByStateItem, LogisticsBySellerItem

router = APIRouter(prefix="/logistics", tags=["Logistics & Supply Chain"])

@router.get("/overview", response_model=StandardResponse[LogisticsOverview])
def get_logistics_overview(db: Session = Depends(get_db)):
    service = LogisticsService(db)
    overview = service.get_overview()
    return StandardResponse(data=overview)

@router.get("/by-state", response_model=StandardResponse[List[LogisticsByStateItem]])
def get_logistics_by_state(db: Session = Depends(get_db)):
    service = LogisticsService(db)
    state_metrics = service.get_by_state()
    return StandardResponse(data=state_metrics)

@router.get("/by-seller", response_model=StandardResponse[List[LogisticsBySellerItem]])
def get_logistics_by_seller(limit: int = Query(20, ge=1, le=100), db: Session = Depends(get_db)):
    service = LogisticsService(db)
    seller_metrics = service.get_by_seller(limit=limit)
    return StandardResponse(data=seller_metrics)
