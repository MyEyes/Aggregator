from app.gui import bp
from flask import render_template, request, redirect, url_for, jsonify
from flask_login import current_user, login_required
from app.models.scan import Scan, ScanResult
from app.models.subject import Subject
from app.models.tool import Tool
from app.models.property import Property, PropertyKind
from app.models import db
from sqlalchemy import desc, asc

@bp.route('/property/kind/<int:id>')
@login_required
def property_kind(id):
    prop = PropertyKind.query.filter_by(id=id).first_or_404()
    return render_template('property/property.html', title='Property Kind - '+prop.name, user=current_user, property=prop)

@bp.route('/property/kind/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_property_kind(id):
    property = PropertyKind.query.filter_by(id=id).first_or_404()
    if request.method == 'GET':
        return render_template('property/edit_property.html', title='Edit Property Kind - '+property.name, user=current_user, property=property)

    data = request.get_json() or {}
    try:
        property.description = data["description"]
        property.name = data["name"]
        db.session.add(property)
        db.session.commit()
        return jsonify({
            "result": "Success",
            "id": property.id
        }
        )
    except Exception as e:
        return jsonify(
                {
                    "result": "Error",
                    "error": str(e)
                }
            )

@bp.route('/property/kind/<int:id>/delete', methods=['GET', 'POST'])
@login_required
def delete_property_kind(id):
    property = PropertyKind.query.filter_by(id=id).first()
    if request.method == 'GET':
        return render_template('property/delete_property.html', title='Delete Property - '+property.name, user=current_user, property=property)

    db.session.delete(property)
    db.session.commit()
    return redirect(url_for('gui.properties_dashboard'))

@bp.route('/property/kind/add', methods=['GET', 'POST'])
@login_required
def add_property_kind():
    if request.method == 'GET':
        return render_template('property/add_property.html', title='Add Property', user=current_user)

    data = request.get_json() or {}
    try:
        newProp = PropertyKind()
        newProp.description = data["description"]
        newProp.name = data["name"]
        db.session.add(newProp)
        db.session.commit()
        return jsonify({
            "result": "Success",
            "id": newProp.id
        }
        )
    except Exception as e:
        return jsonify(
                {
                    "result": "Error",
                    "error": str(e)
                }
            )