from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from backend.app.db.session import get_db
from backend.app.services.customer_service import CustomerService
from backend.app.schemas.common import StandardResponse, PaginatedResponse
from backend.app.schemas.customers import CustomerSegmentItem, CustomerSummaryItem, CustomerGeoItem

router = APIRouter(prefix="/customers", tags=["Customer Intelligence"])

@router.get("/segments", response_model=StandardResponse[List[CustomerSegmentItem]])
def get_customer_segments(db: Session = Depends(get_db)):
    service = CustomerService(db)
    segments = service.get_segments()
    return StandardResponse(data=segments)

@router.get("/geo", response_model=StandardResponse[List[CustomerGeoItem]])
def get_customer_geo_distribution(db: Session = Depends(get_db)):
    service = CustomerService(db)
    geo = service.get_geo_distribution()
    return StandardResponse(data=geo)

@router.get("/list", response_model=PaginatedResponse[CustomerSummaryItem])
def get_customers_list(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    segment: Optional[str] = Query(None),
    state: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    service = CustomerService(db)
    items, meta = service.get_customers_paginated(page=page, page_size=page_size, segment=segment, state=state)
    return PaginatedResponse(data=items, metadata=meta)
