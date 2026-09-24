from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.services.data_quality_service import DataQualityService
from backend.app.schemas.common import StandardResponse
from backend.app.schemas.data_quality import DataQualityOverview

router = APIRouter(prefix="/data-quality", tags=["Data Quality Center"])

@router.get("/overview", response_model=StandardResponse[DataQualityOverview])
def get_data_quality_overview(db: Session = Depends(get_db)):
    service = DataQualityService(db)
    overview = service.get_overview()
    return StandardResponse(data=overview)
