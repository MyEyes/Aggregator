from flask import Blueprint

bp = Blueprint('gui', __name__, static_folder="static", template_folder="templates")

from app.gui import routes, login, dashboard