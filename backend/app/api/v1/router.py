from fastapi import APIRouter
from backend.app.api.v1.dashboard import router as dashboard_router
from backend.app.api.v1.analytics import router as analytics_router
from backend.app.api.v1.customers import router as customers_router
from backend.app.api.v1.products import router as products_router
from backend.app.api.v1.sellers import router as sellers_router
from backend.app.api.v1.logistics import router as logistics_router
from backend.app.api.v1.data_quality import router as data_quality_router
from backend.app.api.v1.ml import router as ml_router
from backend.app.api.v1.ai import router as ai_router

api_v1_router = APIRouter(prefix="/api/v1")

api_v1_router.include_router(dashboard_router)
api_v1_router.include_router(analytics_router)
api_v1_router.include_router(customers_router)
api_v1_router.include_router(products_router)
api_v1_router.include_router(sellers_router)
api_v1_router.include_router(logistics_router)
api_v1_router.include_router(data_quality_router)
api_v1_router.include_router(ml_router)
api_v1_router.include_router(ai_router)
