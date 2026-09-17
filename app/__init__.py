"""
Milijon Railway Panel - Application Package
"""

from flask import Flask
from app.config import Config
from app.database import db
from app.routes import register_routes


def create_app():
    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="static",
    )
    app.config.from_object(Config)

    db.init_app(app)
    register_routes(app)

    return app
