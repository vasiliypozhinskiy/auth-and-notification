import os

SWAGGER_DOCS_PATH = os.getcwd() + "/swagger_docs"

swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": "apispec_1",
            "route": "/auth/apispec_1.json",
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/auth/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/auth/apidocs/",
}

swagger_template = {
    "securityDefinitions":
        {"bearerAuth":
            {
                "type": "apiKey", "name": "authorization", "in": "header"
            }
        }
}
