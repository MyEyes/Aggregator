from app.gui import bp
from flask import render_template, request, redirect, url_for, jsonify
from flask_login import current_user, login_required
from app.models.scan import Scan, ScanResult
from app.models.subject import Subject
from app.models.tool import Tool
from app.models.property import Property, PropertyKind
from app.models import db
from sqlalchemy import desc, asc

@bp.route('/property/<int:id>')
@login_required
def property(id):
    prop = Property.query.filter_by(id=id).first_or_404()
    return render_template('property/property.html', title='Property - '+prop.name, user=current_user, property=prop)