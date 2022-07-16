import os


from app.core import app, db, migrate, Config

from opentelemetry.instrumentation.flask import FlaskInstrumentor

from app.core import app, db, migrate
from app.core.tracing import configure_tracer, tracing_blueprint
from app.views.totp_view import totp_blueprint
from app.views.user_view import user_blueprint
from app.views.oauth_view import oauth_blueprint
from app.views.role_view import role_blueprint
from app.views.user_add_role import user_role_blueprint
from app.views.auth_views import auth_blueprint
from app.views.sample_page import sample_page_blueprint


def create_app(flask_app):
    db.init_app(flask_app)
    flask_app.register_blueprint(role_blueprint)
    flask_app.register_blueprint(user_role_blueprint)
    flask_app.register_blueprint(user_blueprint)
    flask_app.register_blueprint(auth_blueprint)
    flask_app.register_blueprint(oauth_blueprint)
    flask_app.register_blueprint(sample_page_blueprint)
    flask_app.register_blueprint(tracing_blueprint)

    flask_app.register_blueprint(totp_blueprint)
    migrate.init_app(flask_app, db)

    configure_tracer()

    FlaskInstrumentor().instrument_app(flask_app)
    return flask_app


app = create_app(app)


if __name__ == "__main__":
    app.run(
        host=os.getenv('HOST', 'localhost'),
        debug=bool(os.getenv('DEBUG', 1)),
    )

