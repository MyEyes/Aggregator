from app.gui import bp
from flask import render_template, request, redirect, url_for
from flask_login import current_user, login_required
from app.models.scan import Scan, ScanResult
from app.models.subject import Subject
from app.models.tool import Tool

@bp.route('/')
@bp.route('/dashboard')
@login_required
def dashboard():
    return redirect(url_for('gui.scans_dashboard'))

@bp.route('/dashboard/scans')
@login_required
def scans_dashboard():
    return render_template('dashboard/scans.html', title='Dashboard - Scans', user=current_user, scans=Scan.query.all())

@bp.route('/dashboard/subjects')
@login_required
def subjects_dashboard():
    return render_template('dashboard/subjects.html', title='Dashboard - Subjects', user=current_user, subjects = Subject.query.all())

@bp.route('/dashboard/tools')
@login_required
def tools_dashboard():
    return render_template('dashboard/tools.html', title='Dashboard - Tools', user=current_user, tools=Tool.query.all())

@bp.route('/dashboard/results')
@login_required
def results_dashboard():
    return render_template('dashboard/results.html', title='Dashboard - Results', user=current_user, results=ScanResult.query.all())