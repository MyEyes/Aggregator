from flask import Blueprint

bp = Blueprint('gui', __name__, static_folder="static", template_folder="templates")

from app.gui import login, dashboard, scan, subject, result, tags, tree, properties, admin, property_kinds