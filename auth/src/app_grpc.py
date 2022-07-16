from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from app.core.config import Config


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)
    db = SQLAlchemy(app)
    db.init_app(app)
    return app

app_grpc = create_app()
