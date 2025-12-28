import os
from flask import Flask
from flask_cors import CORS
from flask_wtf.csrf import CSRFProtect
from . import db
from . import (
    auth,
    rev_webui,
    challenge,
)


def create_app() -> Flask:
    """
    Application Factory to configure and create the Flask app.
    This function handles setup only. It does NOT start the server.
    """
    app = Flask(__name__, instance_relative_config=True)

    # Determine environment for internal Flask flags
    env = os.getenv("FLASK_ENV", "development")

    if env == "production":
        app.debug = False
        app.config["TESTING"] = False
    else:
        app.debug = True

    # Configuration Mapping
    app.config.from_mapping(
        SECRET_KEY=os.getenv("SECRET_KEY", "dev_secret_key_123"),
        MYSQL_HOST=os.getenv("MYSQL_HOST"),
        MYSQL_USER=os.getenv("MYSQL_USER"),
        MYSQL_PASSWORD=os.getenv("MYSQL_PASSWORD"),
        MYSQL_DATABASE=os.getenv("MYSQL_DATABASE"),
    )

    app.config.update(
        SESSION_COOKIE_SECURE=True,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
    )

    # Initialize CORS
    CORS(app)

    # Initialize CSRF Protection
    csrf = CSRFProtect()
    csrf.init_app(app)

    app.config.from_pyfile("config.py", silent=True)

    db.init_app(app)

    app.register_blueprint(auth.bp)
    app.register_blueprint(rev_webui.bp)
    app.register_blueprint(challenge.bp)

    app.add_url_rule("/", endpoint="index")

    return app
