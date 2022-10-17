from flask import Flask
from app.gui import bp as gui_bp
from app.api import bp as api_bp
from .config import Config
from app.models import db, migrate, login
from flask_bootstrap import Bootstrap

bootstrap = Bootstrap()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.register_blueprint(gui_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    bootstrap.init_app(app)
    return app

from app import models