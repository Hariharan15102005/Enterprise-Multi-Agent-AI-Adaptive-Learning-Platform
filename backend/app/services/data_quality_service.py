from sqlalchemy.orm import Session
from backend.app.repositories.data_quality_repository import DataQualityRepository
from backend.app.schemas.data_quality import DataQualityOverview

class DataQualityService:
    def __init__(self, db: Session):
        self.repo = DataQualityRepository(db)

    def get_overview(self) -> DataQualityOverview:
        data = self.repo.get_data_quality_overview()
        return DataQualityOverview(**data)
