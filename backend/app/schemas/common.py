from typing import Generic, TypeVar, Optional, List, Any
from pydantic import BaseModel, Field

T = TypeVar("T")

class PaginationMetadata(BaseModel):
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)
    total_records: int = Field(0, ge=0)
    total_pages: int = Field(0, ge=0)

class StandardResponse(BaseModel, Generic[T]):
    success: bool = True
    data: T
    metadata: Optional[dict[str, Any]] = None

class PaginatedResponse(BaseModel, Generic[T]):
    success: bool = True
    data: List[T]
    metadata: PaginationMetadata

class ErrorDetail(BaseModel):
    code: str
    message: str
    details: Optional[dict[str, Any]] = None

class ErrorResponse(BaseModel):
    success: bool = False
    error: ErrorDetail
