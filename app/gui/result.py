from app.gui import bp
from flask import render_template, request, redirect, url_for, jsonify
from flask_login import current_user, login_required
from app.models.scan import Scan, ScanResult
from app.models.subject import Subject
from app.models.tool import Tool
from app.models import db

@bp.route('/result/<int:id>/<string:state>', methods=['POST'])
@login_required
def set_state(id, state):
    result = ScanResult.query.filter_by(id=id).first()
    if result:
        result.set_state(state)
        db.session.add(result)
        db.session.commit()
        return jsonify(
            {
                "result": "OK"
            }
        )
    return jsonify(
            {
                "result": "Error",
                "error": "No such result"
            }
        )