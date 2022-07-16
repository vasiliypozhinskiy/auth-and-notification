import aio_pika
import uvicorn
from fastapi import FastAPI, APIRouter
from fastapi.responses import ORJSONResponse
from motor.motor_asyncio import AsyncIOMotorClient

from api import router as api_router
from core.config import Config
from core import services

ROUTERS = (api_router,)

config = Config()


def prepare_app(routers: tuple[APIRouter]) -> FastAPI:

    """Init app, app routes etc."""

    fastapi_app = FastAPI(
        title="notification api",
        docs_url="/notifications/api/openapi",
        openapi_url="/notifications/api/openapi.json",
        default_response_class=ORJSONResponse,
    )
    for router in routers:
        fastapi_app.include_router(router)
    return fastapi_app


app = prepare_app(ROUTERS)


@app.on_event("startup")
async def startup() -> None:

    """Startup hook."""

    services.mongo_client = AsyncIOMotorClient(config.mongo.host, config.mongo.port)
    services.rabbit_connection = await aio_pika.connect(
        host=config.rabbit.host,
        port=config.rabbit.port,
        password=config.rabbit.default_pass,
        login=config.rabbit.default_user
    )


@app.on_event("shutdown")
async def shutdown() -> None:

    """Shutdown hook."""

    await services.rabbit_connection.close()


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        debug=True
    )
