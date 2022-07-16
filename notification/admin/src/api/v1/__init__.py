from fastapi import APIRouter

from api.v1.admin import router as admin_router

router = APIRouter(prefix="/v1")

router.include_router(admin_router)
