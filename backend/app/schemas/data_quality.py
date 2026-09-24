from typing import List, Optional
from pydantic import BaseModel

class DQCheckItem(BaseModel):
    rule: str
    dataset: str
    status: str
    affected_rows: int
    pct_affected: float
    severity: str
    message: str

class DataQualityOverview(BaseModel):
    overall_quality_score: float
    status: str
    total_checks_executed: int
    passed_checks: int
    failed_checks: int
    warning_checks: int
    quarantined_records_count: int
    tables_monitored: int
    total_rows_monitored: int
    checks: List[DQCheckItem]
