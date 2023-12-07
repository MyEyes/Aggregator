from app.gui import bp
from flask import render_template, request, redirect, url_for
from flask_login import current_user, login_required
from sqlalchemy import update

from app.models import db
from app.models.subject import Subject, SubjectAltNames, SubjectAltPaths, SubjectChildTallies, SubjectResultTallies
from app.models.scan import Scan, ScanResult, DuplicateScanResult, ScanResultTallies
from app.models.tag import Tag, result_tags, subject_tags

@bp.route('/dashboard/admin/wipe_db')
@login_required
def wipe_db():
    if not request.args.get('confirmed'):
        return render_template('util/ask_confirm.html', title="Confirm Database Wipe", text='Are you 100% sure you want to wipe the database?')
    # Wipe many-many tables
    db.session.execute(result_tags.delete())
    db.session.execute(subject_tags.delete())
    DuplicateScanResult.query.delete()
    ScanResultTallies.query.delete()

    ScanResult.query.delete()
    Scan.query.delete()

    SubjectAltNames.query.delete()
    SubjectAltPaths.query.delete()
    SubjectChildTallies.query.delete()
    SubjectResultTallies.query.delete()
    Subject.query.update({'parentId': None})
    Subject.query.delete()
    Tag.query.delete()
    db.session.commit()
    return redirect(url_for('gui.scans_dashboard'))

@bp.route('/dashboard/admin/rebuild_caches')
@login_required
def rebuild_caches():
    Subject.calculateCaches()
    return redirect(url_for('gui.subjects_dashboard'))