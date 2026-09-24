"""Centralized custom exception hierarchy for the OlistIQ backend."""

from typing import Optional, Dict, Any


class AppException(Exception):
    """Base application exception."""
    def __init__(
        self,
        message: str,
        code: str = "INTERNAL_SERVER_ERROR",
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}


class ResourceNotFoundException(AppException):
    """Raised when a requested resource (order, customer, seller, model) does not exist."""
    def __init__(self, message: str, resource_type: Optional[str] = None, resource_id: Optional[str] = None):
        super().__init__(
            message=message,
            code="RESOURCE_NOT_FOUND",
            status_code=404,
            details={"resource_type": resource_type, "resource_id": resource_id} if resource_type else {}
        )


class BadRequestException(AppException):
    """Raised when request parameters or payload are semantically invalid."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="BAD_REQUEST",
            status_code=400,
            details=details
        )


class ValidationException(AppException):
    """Raised for business-level validation failures."""
    def __init__(self, message: str, errors: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            status_code=422,
            details={"errors": errors} if errors else {}
        )


class UnauthorizedException(AppException):
    """Raised when an operation is unauthorized."""
    def __init__(self, message: str = "Unauthorized access"):
        super().__init__(
            message=message,
            code="UNAUTHORIZED",
            status_code=401
        )


class DatabaseException(AppException):
    """Raised for sanitized database operational failures."""
    def __init__(self, message: str = "A database operation failed"):
        super().__init__(
            message=message,
            code="DATABASE_ERROR",
            status_code=500
        )
