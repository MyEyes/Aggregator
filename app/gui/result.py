from app.gui import bp
from flask import render_template, request, redirect, url_for, jsonify
from flask_login import current_user, login_required
from app.models.scan import Scan, ScanResult
from app.models.subject import Subject
from app.models.tool import Tool
from app.models import db

@bp.route('/result/<int:id>', methods=['GET'])
@login_required
def result(id):
    result = ScanResult.query.filter_by(id=id).first_or_404()
    soft_matches = ScanResult.query.filter_by(soft_match_hash=result.soft_match_hash)
    return render_template('result/result.html', title="Result", user=current_user, mainresult=result, soft_matches=soft_matches)

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