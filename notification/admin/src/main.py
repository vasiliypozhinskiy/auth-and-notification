import uvicorn
from fastapi import FastAPI, APIRouter
from fastapi.responses import ORJSONResponse
from motor.motor_asyncio import AsyncIOMotorClient

from api import router as api_router
from core.config import config
from db import mongo

ROUTERS = (api_router,)


def prepare_app(routers: tuple[APIRouter]) -> FastAPI:
    """Init app, app routes etc."""
    fastapi_app = FastAPI(
        title="admin notification panel api",
        docs_url="/admin_notifications/api/openapi",
        openapi_url="/admin_notifications/api/openapi.json",
        default_response_class=ORJSONResponse,
    )
    for router in routers:
        fastapi_app.include_router(router)
    return fastapi_app


app = prepare_app(ROUTERS)


@app.on_event("startup")
async def startup() -> None:
    mongo.MONGO_CLIENT = AsyncIOMotorClient(config.db_host, config.db_port)


@app.on_event("shutdown")
async def shutdown() -> None:
    mongo.MONGO_CLIENT.close()


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        debug=True
    )