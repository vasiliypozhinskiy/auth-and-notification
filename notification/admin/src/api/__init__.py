from fastapi import APIRouter

from api.v1 import router as v1_router

router = APIRouter(prefix="/admin_notifications/api")
router.include_router(v1_router)
