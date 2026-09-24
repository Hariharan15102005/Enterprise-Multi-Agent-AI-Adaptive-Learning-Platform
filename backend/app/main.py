"""OlistIQ Enterprise Decision Intelligence Platform — FastAPI Application Main Entry Point."""

import time
from fastapi import FastAPI, Request, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from backend.app.core.config import backend_config
from backend.app.core.logging import logger
from backend.app.core.exceptions import AppException
from backend.app.api.v1.router import api_v1_router

tags_metadata = [
    {
        "name": "System Health",
        "description": "Core operational health check and version metadata endpoints."
    },
    {
        "name": "Executive Dashboard",
        "description": "High-level marketplace KPIs, revenue totals, order counts, and growth metrics."
    },
    {
        "name": "Deep Analytics",
        "description": "Category performance, monthly revenue trends, payment distributions, and operational insights."
    },
    {
        "name": "Customer Intelligence",
        "description": "RFM customer segmentation, geographic distributions, and customer list exploration."
    },
    {
        "name": "Product Intelligence",
        "description": "Product catalog analytics, dimension groupings, and category metrics."
    },
    {
        "name": "Seller Intelligence",
        "description": "Merchant leaderboards, SLA compliance, and seller geographic profiles."
    },
    {
        "name": "Logistics Intelligence",
        "description": "Doorstep delivery durations, on-time rates, and state-level freight analytics."
    },
    {
        "name": "Data Quality & Governance",
        "description": "Warehouse profiling, referential integrity verification, and data quality scores."
    },
    {
        "name": "Machine Learning & Predictive Intelligence",
        "description": "Model registry, RFM clustering, delivery delay classifiers, satisfaction models, and time-series forecasting."
    },
    {
        "name": "AI Analyst / Natural Language to SQL",
        "description": "Conversational business analyst with LangGraph orchestration, query planning, SQL guardrails, and insight synthesis."
    }
]

app = FastAPI(
    title=backend_config.APP_NAME,
    version=backend_config.APP_VERSION,
    description="""
# OlistIQ Decision Intelligence Platform API

An enterprise-grade analytics, machine learning, and AI decision intelligence backend for Brazilian e-commerce analytics (Olist dataset).

## Features
- **Executive Analytics:** Real-time revenue, order volume, customer LTV, and delivery KPIs.
- **Predictive ML Intelligence:** RFM customer segmentation, delay risk classification, review dissatisfaction prediction, and 30-day demand forecasting.
- **Conversational AI Analyst:** LangGraph-driven natural language to SQL engine with multi-layered guardrails.
- **Enterprise Data Warehouse:** Star-schema analytical tables and optimized One Big Table (OBT) views.
    """,
    openapi_tags=tags_metadata,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# -------------------------------------------------------------
# 1. CORS Configuration (Frontend-Ready)
# -------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=backend_config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["X-Process-Time-Ms"]
)

# -------------------------------------------------------------
# 2. Request Timing & Audit Middleware
# -------------------------------------------------------------
@app.middleware("http")
async def add_process_time_and_log(request: Request, call_next):
    start_time = time.perf_counter()
    try:
        response = await call_next(request)
        process_time_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
        response.headers["X-Process-Time-Ms"] = str(process_time_ms)
        logger.info(f"{request.method} {request.url.path} - {response.status_code} ({process_time_ms}ms)")
        return response
    except Exception as exc:
        process_time_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
        logger.error(f"Unhandled Exception on {request.method} {request.url.path} after {process_time_ms}ms: {exc}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "An unexpected internal server error occurred while processing the request.",
                    "details": {}
                }
            },
            headers={"X-Process-Time-Ms": str(process_time_ms)}
        )

# -------------------------------------------------------------
# 3. Centralized Exception Handlers
# -------------------------------------------------------------
@app.exception_handler(AppException)
async def custom_app_exception_handler(request: Request, exc: AppException):
    logger.warning(f"AppException [{exc.code}] on {request.method} {request.url.path}: {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details
            }
        }
    )

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    code_map = {
        400: "BAD_REQUEST",
        401: "UNAUTHORIZED",
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        405: "METHOD_NOT_ALLOWED",
        422: "UNPROCESSABLE_ENTITY",
        500: "INTERNAL_SERVER_ERROR"
    }
    error_code = code_map.get(exc.status_code, "HTTP_ERROR")
    logger.warning(f"HTTPException {exc.status_code} ({error_code}) on {request.method} {request.url.path}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": error_code,
                "message": str(exc.detail),
                "details": {}
            },
            "detail": str(exc.detail)  # Included for standard client compatibility
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    formatted_errors = []
    for err in exc.errors():
        field_path = " -> ".join([str(loc) for loc in err.get("loc", [])])
        formatted_errors.append({
            "field": field_path,
            "message": err.get("msg"),
            "type": err.get("type")
        })
    logger.warning(f"RequestValidationError on {request.method} {request.url.path}: {formatted_errors}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Validation failed for one or more request parameters.",
                "details": {"errors": formatted_errors}
            }
        }
    )

# -------------------------------------------------------------
# 4. Core System Endpoints
# -------------------------------------------------------------
@app.get("/health", tags=["System Health"], summary="System Health & Status")
def health_check():
    """Returns operational status, service metadata, and active environment."""
    return {
        "status": "healthy",
        "service": backend_config.APP_NAME,
        "version": backend_config.APP_VERSION,
        "environment": backend_config.ENVIRONMENT
    }

# -------------------------------------------------------------
# 5. Mount API v1 Router
# -------------------------------------------------------------
app.include_router(api_v1_router)
