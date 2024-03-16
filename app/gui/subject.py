from app.gui import bp
from flask import render_template, request, redirect, url_for, jsonify
from flask_login import current_user, login_required
from app.models.scan import Scan, ScanResult
from app.models.subject import Subject
from app.models.tool import Tool
from app.models.tag import Tag
from app.models import db
from sqlalchemy import desc, asc

@bp.route('/subject/<int:id>')
@login_required
def subject(id):
    _subject = Subject.query.filter_by(id=id).first()
    soft_matches = _subject.get_soft_matches()
    results = ScanResult.query.filter_by(subject_id=_subject.id)
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
    tags = Tag.query.all()
    return render_template('subject/subject.html', title='Subject - '+_subject.name, user=current_user, results = results, subject=_subject, soft_matches=soft_matches, sort=_sort, sort_op=_sort_op, valid_tags=tags)

@bp.route('/subject/<int:id>/notes', methods=['POST'])
@login_required
def set_subj_notes(id):
    result = Subject.query.filter_by(id=id).first()
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

@bp.route('/subject/<int:id>/add-tag', methods=['POST'])
@login_required
def add_subject_tag(id):
    subject = Subject.query.filter_by(id=id).first_or_404()
    data = request.get_json() or {}
    tag = Tag.query.filter_by(id=data["tag_id"]).first_or_404()
    if tag:
        if tag not in subject.tags:
            subject.tags.append(tag)
            subject.touch()
            db.session.add(subject)
            db.session.commit()
        return jsonify(
                {
                    "result": "OK"
                }
            )
    return jsonify(
            {
                "result": "Error",
                "error": "No such subject"
            }
        )

@bp.route('/subject/<int:id>/del-tag', methods=['POST'])
@login_required
def del_subject_tag(id):
    subject = Subject.query.filter_by(id=id).first_or_404()
    data = request.get_json() or {}
    tag = Tag.query.filter_by(id=data["tag_id"]).first_or_404()
    if tag:
        if tag in subject.tags:
            subject.tags.remove(tag)
            subject.touch()
            db.session.add(subject)
            db.session.commit()
        return jsonify(
                {
                    "result": "OK"
                }
            )
    return jsonify(
            {
                "result": "Error",
                "error": "No such subject"
            }
        )

@bp.route('/subject/<int:id>/transfer-tags', methods=['POST'])
@login_required
def subject_transfer_tags_to_soft_matches(id):
    subject = Subject.query.filter_by(id=id).first_or_404()
    soft_matches = subject.get_soft_matches()
    return jsonify(
        {
            "result": "OK"
        }
    )