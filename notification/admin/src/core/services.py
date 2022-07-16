from http import HTTPStatus

import aiohttp
from aiohttp.client_exceptions import ContentTypeError
from fastapi import Header
from jinja2 import Template

from db.mongo import get_mongo_client

from core.config import config, TEMPLATE_AVAILABLE_VARIABLES


def template_validation(template, used_variables_names):
    if not all(variable_name in TEMPLATE_AVAILABLE_VARIABLES for variable_name in used_variables_names):
        return False

    if template:
        try:
            jinja_template = Template(template)

            required_variables = {}
            for variable_name in used_variables_names:
                required_variables.update({variable_name: TEMPLATE_AVAILABLE_VARIABLES[variable_name]})

            jinja_template.render(required_variables)
        except Exception:
            return False
        return True

    return False


async def save_template_to_db(template, required_variables):
    client = get_mongo_client()
    collection = client.notification.templates

    result = await collection.insert_one({'body': template, 'required_variables': required_variables})

    return str(result.inserted_id)


async def sent_to_notification_api(
    data,
    x_request_id: str | None = Header(None)
):
    async with aiohttp.ClientSession(
        headers={
            "X-Request-Id": x_request_id,
            "Content-Type": "application/json"
        }
    ) as session:
        async with session.post(url=config.notification_api_url, json=data) as response:
            if response.status == HTTPStatus.OK:
                return await response.json()
            else:
                return {"notification_api_status": response.status, "reason": response.reason}
