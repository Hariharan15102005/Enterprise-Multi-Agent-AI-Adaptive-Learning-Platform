from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from backend.app.db.session import get_db
from backend.app.services.seller_service import SellerService
from backend.app.schemas.common import PaginatedResponse
from backend.app.schemas.sellers import SellerAnalyticsItem

router = APIRouter(prefix="/sellers", tags=["Seller Intelligence"])

@router.get("/leaderboard", response_model=PaginatedResponse[SellerAnalyticsItem])
def get_sellers_leaderboard(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    tier: Optional[str] = Query(None),
    state: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    service = SellerService(db)
    items, meta = service.get_sellers_paginated(page=page, page_size=page_size, tier=tier, state=state)
    return PaginatedResponse(data=items, metadata=meta)
