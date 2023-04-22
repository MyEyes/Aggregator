from app.gui import bp
from flask import render_template, request, redirect, url_for, jsonify
from flask_login import current_user, login_required
from app.models.scan import Scan, ScanResult
from app.models.subject import Subject
from app.models.tool import Tool
from app.models import db
from sqlalchemy import desc, asc

@bp.route('/subject/<int:id>')
@login_required
def subject(id):
    subject = Subject.query.filter_by(id=id).first()
    soft_matches = Subject.query.filter_by(soft_match_hash=subject.soft_match_hash)
    results = ScanResult.query.filter_by(subject_id=subject.id)
    _sort_op = "desc"
    if "sort_op" in request.args:
        _sort_op = request.args["sort_op"]
    _sort = "created_at"
    if "sort" in request.args:
        _sort = request.args['sort']
        __sort = _sort
        if _sort == "subject":
            results = results.join(ScanResult.subject)
            __sort = "name"
        if _sort_op == "asc":
            results = results.order_by(asc(__sort))
        else:
            results = results.order_by(desc(__sort))
    return render_template('subject/subject.html', title='Subject - '+subject.name, user=current_user, results = results, subject=subject, soft_matches=soft_matches, sort=_sort, sort_op=_sort_op)

@bp.route('/subject/<int:id>/notes', methods=['POST'])
@login_required
def set_subj_notes(id):
    result = Subject.query.filter_by(id=id).first()
    data = request.get_json() or {}
    if result and data["notes"]:
        result.set_note(data["notes"])
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