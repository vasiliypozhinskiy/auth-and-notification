from http import HTTPStatus

from fastapi import APIRouter, Header
from fastapi.responses import JSONResponse

from core.services import save_template_to_db, sent_to_notification_api, template_validation
from models.models import AdminRequest

router = APIRouter()


@router.post("/", description="")
async def admin(
    request_data: AdminRequest,
    x_request_id: str | None = Header(None)
):
    if not template_validation(request_data.template, request_data.variables):
        return JSONResponse(
            status_code=HTTPStatus.BAD_REQUEST,
            content={"message": "invalid template"}
        )

    ids = [str(i) for i in request_data.user_id]
    template_id = await save_template_to_db(request_data.template, request_data.variables)
    data = {
        "event": "thematic_send",
        "user_id": ids,
        "template_id": template_id
    }

    response = await sent_to_notification_api(
        data=data,
        x_request_id=x_request_id
    )
    return response
