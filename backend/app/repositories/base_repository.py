from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Any, List, Dict, Optional

class BaseRepository:
    def __init__(self, db: Session):
        self.db = db

    def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        result = self.db.execute(text(query), params or {})
        keys = result.keys()
        return [dict(zip(keys, row)) for row in result.fetchall()]

    def execute_scalar(self, query: str, params: Optional[Dict[str, Any]] = None) -> Any:
        result = self.db.execute(text(query), params or {})
        return result.scalar()
