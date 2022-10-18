from app.gui import bp
from flask import render_template, request, redirect, url_for
from flask_login import current_user, login_required
from app.models.scan import Scan, ScanResult
from app.models.subject import Subject
from app.models.tool import Tool

@bp.route('/subject/<int:id>')
@login_required
def subject(id):
    subject = Subject.query.filter_by(id=id).first()
    soft_matches = Subject.query.filter_by(soft_match_hash=subject.soft_match_hash)
    return render_template('subject/subject.html', title='Subject - '+subject.name, user=current_user, subject=subject, soft_matches=soft_matches)