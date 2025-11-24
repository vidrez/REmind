import os
from flask import Flask
from flask_cors import CORS


def create_app() -> Flask:
    """Application Factory to configure and create the Flask app."""

    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(
        SECRET_KEY=os.getenv("SECRET_KEY", "dev"),
        MYSQL_HOST=os.getenv("MYSQL_HOST"),
        MYSQL_USER=os.getenv("MYSQL_USER"),
        MYSQL_PASSWORD=os.getenv("MYSQL_PASSWORD"),
        MYSQL_DATABASE=os.getenv("MYSQL_DATABASE"),
    )

    CORS(app)

    app.config.from_pyfile("config.py", silent=True)

    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Initialize Plugins
    from . import db

    db.init_app(app)

    # Register Blueprints
    from . import auth, rev_webui, first_chall, fourth_chall, fifth_chall, seventh_chall

    blueprints = [
        auth.bp,
        rev_webui.bp,
        first_chall.bp,
        fourth_chall.bp,
        fifth_chall.bp,
        seventh_chall.bp,
    ]

    for bp in blueprints:
        app.register_blueprint(bp)

    app.add_url_rule("/", endpoint="index")

    return app
