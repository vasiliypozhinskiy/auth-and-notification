import json
from aio_pika import Message

from fastapi import APIRouter, Depends, Header
from fastapi.responses import JSONResponse

from core.config import Config
from core.services import get_data_from_auth, get_rabbit_connection
from models.models import AuthRequest

router = APIRouter(prefix="/instant", tags=["Instant notifications"])

config = Config()


@router.post("/", name="Instant notifications")
async def instant_notifications(
        request_data: AuthRequest,
        x_request_id: str | None = Header(None),
        user=Depends(get_data_from_auth),
        rabbit_connection=Depends(get_rabbit_connection)):

    user = user[0]

    to_rabbit = {
        "email": user["email"],
        "first_name": user["first_name"],
        "last_name": user["last_name"],
        "username": user["username"],
        "confirmation_link": request_data.confirmation_link
    }

    channel = await rabbit_connection.channel()
    exchange = await channel.get_exchange("email_notification", ensure=True)

    rabbit_response = await exchange.publish(
        Message(body=json.dumps(to_rabbit).encode('utf-8'),
                headers={"x_request_id": x_request_id}),
        routing_key="email_confirm"
    )

    if rabbit_response.delivery_tag:
        return JSONResponse(
            status_code=200,
            content={"message": "data were added to rabbit"}
        )

    return JSONResponse(
        status_code=400,
        content={"message": "error"}
    )
