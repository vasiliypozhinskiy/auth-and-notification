from fastapi import APIRouter

from api.v1.instant import router as instant_router
from api.v1.regular import router as regular_router
from api.v1.thematic import router as thematic_router


router = APIRouter(prefix="/v1")
router.include_router(instant_router)
router.include_router(regular_router)
router.include_router(thematic_router)
