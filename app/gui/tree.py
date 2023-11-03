from app.gui import bp
from flask import render_template, request, redirect, url_for, jsonify
from flask_login import current_user, login_required
from app.models.scan import Scan, ScanResult
from app.models.subject import Subject
from app.models.tool import Tool
from app.models.tag import Tag
from app.models import db
from sqlalchemy import desc, asc

@bp.route('/tree/subject/<int:id>')
@login_required
def tree_subject(id):
    _subject = Subject.query.filter_by(id=id).first()
    return tree(title=f"Tree - Subject {_subject.id} - '{_subject.name}'", subjects=[_subject])

@bp.route('/tree/subject_matched/<int:id>')
@login_required
def tree_subject_matched(id):
    _subject = Subject.query.filter_by(id=id).first()
    return tree(title=f"Tree - Subject {_subject.id} - Soft Matches", subjects=[_subject, *_subject.get_soft_matches()])

@bp.route('/tree/api/subject/<int:id>/children')
@login_required
def tree_api_subject_children(id):
    _subject = Subject.query.filter_by(id=id).first()
    children = [{'id':c.id, 'name':c.name, 'childNum': len(c.children), 'resultNum': c.results.count(), 'tags':[{'id': t.id, 'shortname':t.shortname, 'color':t.color} for t in c.tags]} for c in _subject.children]
    return jsonify({
            "result": "Success",
            "children": children
        })

@bp.route('/tree/api/subject/<int:id>/results')
@login_required
def tree_api_subject_results(id):
    _subject = Subject.query.filter_by(id=id).first()
    results = [{'id':r.id, 'title':r.title, 'tags':[{'id': t.id, 'shortname':t.shortname, 'color':t.color} for t in r.tags]} for r in _subject.results]
    return jsonify({
            "result": "Success",
            "results": results
        })

@bp.route('/tree/api/result/<int:id>')
@login_required
def tree_api_result(id):
    return jsonify({"result": "Success"})


def tree(title, subjects):
    return render_template('tree/tree.html', title=title, user=current_user, subjects=subjects)