from app.gui import bp
from flask import render_template, request, redirect, url_for, jsonify
from flask_login import current_user, login_required
from app.models.scan import Scan, ScanResult
from app.models.subject import Subject
from app.models.tool import Tool
from app.models.tag import Tag
from app.models import db
from .breadcrumb import Breadcrumb
from sqlalchemy import desc, asc

@bp.route('/tag/<int:id>')
@login_required
def tag(id):
    tag = Tag.query.filter_by(id=id).first()
    breadcrumbs = [Breadcrumb("Dashboard", url_for("gui.dashboard")), Breadcrumb("Tags", url_for("gui.tags_dashboard")), Breadcrumb(str(id))]
    return render_template('tag/tag.html', title='Tag - '+tag.name, breadcrumbs=breadcrumbs, user=current_user, tag=tag)

@bp.route('/tag/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_tag(id):
    tag = Tag.query.filter_by(id=id).first()
    if request.method == 'GET':
        breadcrumbs = [Breadcrumb("Dashboard", url_for("gui.dashboard")), Breadcrumb("Tags", url_for("gui.tags_dashboard")), Breadcrumb(str(id), url_for("gui.tag",id=id)), Breadcrumb("Edit")]
        return render_template('tag/edit_tag.html', title='Edit Tag - '+tag.name, breadcrumbs=breadcrumbs, user=current_user, tag=tag)

    data = request.get_json() or {}
    try:
        tag.color = data["color"]
        tag.description = data["description"]
        tag.name = data["name"]
        tag.shortname = data["shortname"]
        db.session.add(tag)
        db.session.commit()
        return jsonify({
            "result": "Success",
            "id": tag.id
        }
        )
    except Exception as e:
        return jsonify(
                {
                    "result": "Error",
                    "error": str(e)
                }
            )

@bp.route('/tag/<int:id>/delete', methods=['GET', 'POST'])
@login_required
def delete_tag(id):
    tag = Tag.query.filter_by(id=id).first()
    if request.method == 'GET':
        breadcrumbs = [Breadcrumb("Dashboard", url_for("gui.dashboard")), Breadcrumb("Tags", url_for("gui.tags_dashboard")), Breadcrumb(str(id), url_for("gui.tag",id=id)), Breadcrumb("Delete")]
        return render_template('tag/delete_tag.html', title='Delete Tag - '+tag.name, breadcrumbs=breadcrumbs, user=current_user, tag=tag)

    db.session.delete(tag)
    db.session.commit()
    return redirect(url_for('gui.tags_dashboard'))

@bp.route('/tag/add', methods=['GET', 'POST'])
@login_required
def add_tag():
    if request.method == 'GET':
        breadcrumbs = [Breadcrumb("Dashboard", url_for("gui.dashboard")), Breadcrumb("Tags", url_for("gui.tags_dashboard")), Breadcrumb("Add")]
        return render_template('tag/add_tag.html', title='Add Tag', breadcrumbs=breadcrumbs, user=current_user)

    data = request.get_json() or {}
    try:
        newTag = Tag()
        newTag.color = data["color"]
        newTag.description = data["description"]
        newTag.name = data["name"]
        newTag.shortname = data["shortname"]
        db.session.add(newTag)
        db.session.commit()
        return jsonify({
            "result": "Success",
            "id": newTag.id
        }
        )
    except Exception as e:
        return jsonify(
                {
                    "result": "Error",
                    "error": str(e)
                }
            )