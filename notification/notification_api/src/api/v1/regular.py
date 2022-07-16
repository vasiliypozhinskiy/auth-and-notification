from datetime import datetime
from uuid import uuid4

from fastapi import APIRouter, Depends, Header
from fastapi.responses import JSONResponse

from core.config import Config
from core.services import get_data_from_auth, get_mongo_client
from models.models import UgcRequest

router = APIRouter(prefix="/regular", tags=["Regular notifications"])

config = Config()


@router.post("/like", name="Daily likes notification")
async def regular_notifications(
        request_data: UgcRequest,
        x_request_id: str | None = Header(None),
        mongo=Depends(get_mongo_client),
        user_data=Depends(get_data_from_auth)):
    coll = mongo.notifications.regular

    if not user_data[0]:
        return JSONResponse(
            status_code=400,
            content={"message": "user is disabled notifications"}
        )

    if user_data[0] is None:
        return JSONResponse(
            status_code=400,
            content={"message": "user_id incorrect"}
        )

    user = user_data[0]
    already_in_mongo = await coll.find_one(
        {
            "event": request_data.event,
            "$where": "this.sent_to_rabbit_at < this.updated_at",
            "user_id": str(request_data.user_id),
            "content_id": str(request_data.content_id)
        }
    )

    if not already_in_mongo:
        to_mongo = {
            "event": request_data.event,
            "notification_id": str(uuid4()),
            "user_id": str(request_data.user_id),
            "content_id": str(request_data.content_id),
            "sent_to_rabbit_at": datetime.min,
            "updated_at": datetime.now(),
            "time_zone": user["time_zone"],
            "x_request_id": x_request_id,
            "data": {
                "email": user["email"],
                "first_name": user["first_name"],
                "last_name": user["last_name"],
                "username": user["username"],
                "likes_number": 1
            }
        }

        try:
            await coll.insert_one(to_mongo)
            return JSONResponse(
                status_code=200,
                content={"message": "data were added to mongo"}
            )
        except Exception as exp:
            return JSONResponse(
                status_code=400,
                content={"message": repr(exp)}
            )

    mongo_id = already_in_mongo["_id"]
    already_in_mongo["data"]["likes_number"] += 1
    already_in_mongo["updated_at"] = datetime.now()
    try:
        await coll.replace_one({"_id": mongo_id}, already_in_mongo)
        return JSONResponse(
            status_code=200,
            content={"message": "data updated"}
        )
    except Exception as exp:
        return JSONResponse(
            status_code=400,
            content={"message": repr(exp)}
        )
