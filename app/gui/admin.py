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
    Scan.update_all_result_tag_tallies()
    return redirect(url_for('gui.subjects_dashboard'))

@bp.route('/dashboard/admin/transfer_result_tags')
@login_required
def admin_transfer_result_tags():
    ScanResult.transfer_soft_tags()
    Subject.calculateCaches()
    Scan.update_all_result_tag_tallies()
    db.session.commit()
    return redirect(url_for('gui.scans_dashboard'))


@bp.route('/dashboard/admin/tally_subjects')
@login_required
def subject_depth():
    raw_sql = """
    UPDATE subject SET depth=0 WHERE parentId is NULL;
    """
    db.session.execute(raw_sql)
    depth = 1

    while True:
        raw_sql = """
        UPDATE subject INNER JOIN subject parent ON parent.id=subject.parentId  SET subject.depth=:depth WHERE parent.depth=:depthm1;
        """
        try:
            result = db.session.execute(raw_sql, {'depth':depth, 'depthm1':depth-1})
            if result.rowcount==0:
                break
            depth+=1
        except Exception:
            break
    db.session.commit()
    return redirect(url_for('gui.subjects_dashboard'))