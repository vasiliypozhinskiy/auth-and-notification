from datetime import datetime
from uuid import uuid4

from fastapi import APIRouter, Depends, Header
from fastapi.responses import JSONResponse

from core.config import Config
from core.services import get_data_from_auth, get_mongo_client
from models.models import AdminRequest

router = APIRouter(prefix="/thematic", tags=["Thematic notifications"])

config = Config()


@router.post("/", name="Thematic notifications")
async def thematic_notifications(request_data: AdminRequest,
                                 x_request_id: str | None = Header(None),
                                 mongo=Depends(get_mongo_client),
                                 users=Depends(get_data_from_auth)):
    coll = mongo.notifications.thematic

    for user in users:
        if user is None or not user["notification"]:
            continue

        to_mongo = {
            "event": request_data.event,
            "notification_id": str(uuid4()),
            "user_id": str(user["uuid"]),
            "sent_to_rabbit_at": datetime.min,
            "updated_at": datetime.now(),
            "time_zone": user["time_zone"],
            "x_request_id": x_request_id,
            "data": {
                "email": user["email"],
                "first_name": user["first_name"],
                "last_name": user["last_name"],
                "username": user["username"],
                "template_id": request_data.template_id
            }
        }

        try:
            coll.insert_one(to_mongo)
        except Exception as exp:
            return JSONResponse(
                status_code=400,
                content={"message": repr(exp)}
            )

    return JSONResponse(
        status_code=200,
        content={"message": "data were added to mongo"}
    )
