from app.core.config import Config, TEMPLATE_FOLDER
from app.core.swagger_config import swagger_config, swagger_template
from flasgger import Swagger
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


app = Flask(
    __name__,
    instance_relative_config=True,
    template_folder=TEMPLATE_FOLDER
)

app.config.from_object(Config)

db = SQLAlchemy(app)

swagger = Swagger(app, config=swagger_config, template=swagger_template)

migrate = Migrate(app, db)
