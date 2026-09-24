from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from backend.app.db.session import get_db
from backend.app.services.product_service import ProductService
from backend.app.schemas.common import PaginatedResponse
from backend.app.schemas.products import ProductAnalyticsItem

router = APIRouter(prefix="/products", tags=["Product Intelligence"])

@router.get("/list", response_model=PaginatedResponse[ProductAnalyticsItem])
def get_products_list(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category: Optional[str] = Query(None),
    sort_by: str = Query("items_sold", pattern="^(items_sold|gmv)$"),
    db: Session = Depends(get_db)
):
    service = ProductService(db)
    items, meta = service.get_products_paginated(page=page, page_size=page_size, category=category, sort_by=sort_by)
    return PaginatedResponse(data=items, metadata=meta)
