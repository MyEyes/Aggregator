from app.gui import bp
from flask import render_template, request, redirect, url_for, jsonify
from flask_login import current_user, login_required
from app.models import db
from app.models.scan import Scan, ScanResult
from app.models.subject import Subject
from app.models.tool import Tool
from sqlalchemy import desc, asc

@bp.route('/scan/<int:id>')
@login_required
def scan(id):
    scan = Scan.query.filter_by(id=id).first()
    return render_template('scan/scan.html', title=str(scan), user=current_user, scan=scan)

@bp.route('/scan/<int:id>/transfer-tags')
@login_required
def scan_transfer_tags(id):
    scan = Scan.query.filter_by(id=id).first()
    scan.transfer_result_tags_to_soft_matches()
    Subject.calculateScanCaches(id)
    db.session.commit()
    return jsonify(
                {
                    "result": "OK"
                }
            )

@bp.route('/scan/<int:id>/delete')
@login_required
def scan_delete(id):
    scan = Scan.query.filter_by(id=id).first_or_404()
    scan.delete()
    Subject.calculateCaches()
    db.session.commit()
    return redirect(url_for('gui.scans_dashboard'))