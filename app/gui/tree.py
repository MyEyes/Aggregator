from app.gui import bp
from flask import render_template, request, redirect, url_for, jsonify
from flask_login import current_user, login_required
from app.models.scan import Scan, ScanResult
from app.models.subject import Subject
from app.models.tool import Tool
from app.models.tag import Tag
from app.models import db
from sqlalchemy import desc, asc
from .breadcrumb import Breadcrumb

@bp.route('/tree/subject/<int:id>')
@login_required
def tree_subject(id):
    _subject = Subject.query.filter_by(id=id).first()
    breadcrumbs = [Breadcrumb("Dashboard", url_for("gui.dashboard")),
                    Breadcrumb("Subjects", url_for("gui.subjects_dashboard")),
                    Breadcrumb(str(id), url_for("gui.subject", id=id)),
                    Breadcrumb("Treeview")]
    return render_template('tree/tree.html', title=f"Tree - Subject {_subject.id} - '{_subject.name}'", subjects=[_subject], breadcrumbs=breadcrumbs)

@bp.route('/tree/subject/<int:id1>/diff/<int:id2>')
@login_required
def tree_subject_diff(id1, id2):
    title = f"Diff Subject {id1} <-> {id2}"
    if id1==id2:
        return tree_error(title, "Subjects must not be the same")
    breadcrumbs = [Breadcrumb("Dashboard", url_for("gui.dashboard")),
                Breadcrumb("Subjects", url_for("gui.subjects_dashboard")),
                Breadcrumb(str(id1), url_for("gui.subject", id=id1)),
                Breadcrumb(f"Treediff w/ {id2}")]
    _subject1 = Subject.query.filter_by(id=id1).first_or_404()
    _subject2 = Subject.query.filter_by(id=id2).first_or_404()
    if _subject1.id not in _subject2.get_soft_match_ids():
        return tree_error(title, "Subjects aren't soft matches of each other")
    return render_template('tree/tree_diff.html', title=title, user=current_user, subject1=_subject1, subject2=_subject2, breadcrumbs=breadcrumbs)

@bp.route('/tree/subject/<int:id1>/comp/<int:id2>')
@login_required
def tree_subject_comp(id1, id2):
    title = f"Comp Subject {id1} <-> {id2}"
    _subject1 = Subject.query.filter_by(id=id1).first_or_404()
    _subject2 = Subject.query.filter_by(id=id2).first_or_404()
    breadcrumbs = [Breadcrumb("Dashboard", url_for("gui.dashboard")),
            Breadcrumb("Subjects", url_for("gui.subjects_dashboard")),
            Breadcrumb(str(id1), url_for("gui.subject", id=id1)),
            Breadcrumb(f"Treecomp w/ {id2}")]
    return render_template('tree/tree_comp.html', title=title, user=current_user, subject1=_subject1, subject2=_subject2, breadcrumbs=breadcrumbs)

def tree_error(title, s):
    return render_template('tree/tree_error.html', title=title, user=current_user, error_text=s)

@bp.route('/tree/api/subject/<int:id>/children')
@login_required
def tree_api_subject_children(id):
    _subject = Subject.query.filter_by(id=id).first()
    children = [{'id':c.id, 'soft_ids':c.get_soft_match_ids(), 'name':c.name, 'childNum': len(c.children), 'resultNum': c.results.count(), 'tags':[{'id': t.id, 'shortname':t.shortname, 'color':t.color} for t in c.tags]} for c in _subject.children]
    return jsonify({
            "result": "Success",
            "children": children
        })

@bp.route('/tree/api/subject/<int:id>/results')
@login_required
def tree_api_subject_results(id):
    _subject = Subject.query.filter_by(id=id).first()
    results = [{'id':r.id, 'soft_ids':r.get_soft_match_ids(), 'title':r.title, 'tags':[{'id': t.id, 'shortname':t.shortname, 'color':t.color} for t in r.tags]} for r in _subject.results]
    return jsonify({
            "result": "Success",
            "results": results
        })

@bp.route('/tree/api/result/<int:id>')
@login_required
def tree_api_result(id):
    return jsonify({"result": "Success"})