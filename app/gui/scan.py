from app.gui import bp
from flask import render_template, request, redirect, url_for
from flask_login import current_user, login_required
from app.models.scan import Scan, ScanResult
from app.models.subject import Subject
from app.models.tool import Tool

@bp.route('/scan/<int:id>')
@login_required
def scan(id):
    scan = Scan.query.filter_by(id=id).first()
    return render_template('scan/scan.html', title='Scan - '+scan.tool.name, user=current_user, scan=scan)