from app.gui import bp
from flask import render_template, request, redirect, url_for, jsonify
from flask_login import current_user, login_required
from app.models.scan import Scan, ScanResult
from app.models.subject import Subject
from app.models.tool import Tool
from app.models.tag import Tag
from app.models import db
from sqlalchemy import update, alias

@bp.route('/result/<int:id>', methods=['GET'])
@login_required
def result(id):
    result = ScanResult.query.filter_by(id=id).first_or_404()
    soft_matches = ScanResult.query.filter_by(soft_match_hash=result.soft_match_hash)
    tags = Tag.query.all()
    return render_template('result/result.html', title="Result", user=current_user, mainresult=result, soft_matches=soft_matches, valid_tags=tags)

@bp.route('/result/<string:new_state>', methods=['POST'])
@login_required
def set_state_filter(new_state):
    stmt = update(ScanResult)
    if "scan_id" in request.form and request.form["scan_id"]:
        stmt = stmt.where(ScanResult.scan_id == request.form["scan_id"])
    if "risk" in request.form and request.form["risk"]:
        stmt = stmt.where(ScanResult.scan_risk_text == request.form["risk"])
    if "state" in request.form and request.form["state"]:
        stmt = stmt.where(ScanResult.state == request.form["state"])
    if "subject_id" in request.form and request.form["subject_id"]:
        stmt = stmt.where(ScanResult.subject_id == request.form["subject_id"])
    stmt = stmt.values(state=new_state)
    db.session.execute(stmt)
    db.session.commit()
    return jsonify(
        {
            "result": "OK"
        }
    )

def _gen_soft_set_statement(state_val, form):
    aliased = alias(ScanResult)
    stmt = update(ScanResult)
    stmt = stmt.where(ScanResult.state == "open")
    if "scan_id" in form and form["scan_id"]:
        subquery = db.session.query(aliased.c.soft_match_hash).filter(aliased.c.scan_id!=form["scan_id"]).filter(aliased.c.state == state_val)
        stmt = stmt.where(ScanResult.scan_id == form["scan_id"])
        stmt = stmt.where(ScanResult.soft_match_hash.in_(subquery))
    if "subject_id" in form and form["subject_id"]:
        subquery = db.session.query(aliased.c.soft_match_hash).filter(aliased.c.subject_id!=form["subject_id"]).filter(aliased.c.state == state_val)
        stmt = stmt.where(ScanResult.subject_id == form["subject_id"])
        stmt = stmt.where(ScanResult.soft_match_hash.in_(subquery))
    stmt = stmt.values(state=state_val)
    return stmt

@bp.route('/result/<int:id>/notes', methods=['POST'])
@login_required
def set_notes(id):
    result = ScanResult.query.filter_by(id=id).first()
    data = request.get_json() or {}
    if result and data["notes"]:
        result.set_note(data["notes"])
        result.touch()
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

@bp.route('/result/<int:id>/add-tag', methods=['POST'])
@login_required
def add_result_tag(id):
    result = ScanResult.query.filter_by(id=id).first_or_404()
    data = request.get_json() or {}
    tag = Tag.query.filter_by(id=data["tag_id"]).first_or_404()
    if tag:
        if tag not in result.tags:
            result.tags.append(tag)
            result.touch()
            db.session.add(result)
            result.subject._recalculateTallies()
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

@bp.route('/result/<int:id>/export-tags')
@login_required
def export_result_tags_to_soft_matches(id):
    result = ScanResult.query.filter_by(id=id).first_or_404()
    result.transfer_tags_to_soft_matches(export=True)
    db.session.commit()
    return redirect(url_for('gui.result', id=id))

@bp.route('/result/<int:id>/import-tags')
@login_required
def import_result_tags_from_soft_matches(id):
    result = ScanResult.query.filter_by(id=id).first_or_404()
    result.transfer_tags_to_soft_matches(export=False)
    db.session.commit()
    return redirect(url_for('gui.result', id=id))

@bp.route('/result/<int:id>/delete')
@login_required
def result_delete(id):
    result = ScanResult.query.filter_by(id=id).first_or_404()
    result.delete()
    db.session.commit()
    return redirect(url_for('gui.results_dashboard'))

@bp.route('/result/<int:id>/del-tag', methods=['POST'])
@login_required
def del_result_tag(id):
    result = ScanResult.query.filter_by(id=id).first_or_404()
    data = request.get_json() or {}
    tag = Tag.query.filter_by(id=data["tag_id"]).first_or_404()
    if tag:
        if tag in result.tags:
            result.tags.remove(tag)
            result.touch()
            db.session.add(result)
            result.subject._recalculateTallies()
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