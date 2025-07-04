from app.gui import bp
from flask import render_template, request, redirect, url_for
from flask_login import current_user, login_required
from app.models.scan import Scan, ScanResult
from app.models.subject import Subject
from app.models.tool import Tool
from app.models.property import Property, PropertyKind
from app.models.tag import Tag
from .breadcrumb import Breadcrumb
from .filtersort import FilterSort

@bp.route('/')
@bp.route('/dashboard')
@login_required
def dashboard():
    return redirect(url_for('gui.scans_dashboard'))

@bp.route('/dashboard/scans')
@login_required
def scans_dashboard():
    filterInfo, scans = FilterSort.filterFromRequest(request, Scan)
    breadcrumbs = [Breadcrumb("Dashboard", url_for("gui.dashboard")), Breadcrumb("Scans")]
    return render_template('dashboard/scans.html', title='Dashboard - Scans', breadcrumbs=breadcrumbs, user=current_user, scans=scans, filterInfo=filterInfo)

@bp.route('/dashboard/subjects')
@login_required
def subjects_dashboard():
    filterInfo, subjects = FilterSort.filterFromRequest(request, Subject)
    tags = Tag.query.all()
    breadcrumbs = [Breadcrumb("Dashboard", url_for("gui.dashboard")), Breadcrumb("Subjects")]
    return render_template('dashboard/subjects.html', title='Dashboard - Subjects', breadcrumbs=breadcrumbs, user=current_user, subjects = subjects, filterInfo=filterInfo, valid_tags=tags)

@bp.route('/dashboard/tools')
@login_required
def tools_dashboard():
    filterInfo, tools = FilterSort.filterFromRequest(request,Tool)
    breadcrumbs = [Breadcrumb("Dashboard", url_for("gui.dashboard")), Breadcrumb("Tools")]
    return render_template('dashboard/tools.html', title='Dashboard - Tools', breadcrumbs=breadcrumbs, user=current_user, tools=tools, filterInfo=filterInfo)

@bp.route('/dashboard/tags')
@login_required
def tags_dashboard():
    filterInfo, tags = FilterSort.filterFromRequest(request, Tag)
    breadcrumbs = [Breadcrumb("Dashboard", url_for("gui.dashboard")), Breadcrumb("Tags")]
    return render_template('dashboard/tags.html', title='Dashboard - Tags', breadcrumbs=breadcrumbs, user=current_user, tags=tags, filterInfo=filterInfo)

@bp.route('/dashboard/properties')
@login_required
def properties_dashboard():
    filterInfo, properties = FilterSort.filterFromRequest(request, PropertyKind)
    breadcrumbs = [Breadcrumb("Dashboard", url_for("gui.dashboard")), Breadcrumb("Properties")]
    return render_template('dashboard/properties.html', title='Dashboard - Properties', breadcrumbs=breadcrumbs, user=current_user, properties=properties, filterInfo=filterInfo)

@bp.route('/dashboard/results')
@login_required
def results_dashboard():
    filterInfo, results = FilterSort.filterFromRequest(request, ScanResult)
    tags = Tag.query.all()
    breadcrumbs = [Breadcrumb("Dashboard", url_for("gui.dashboard")), Breadcrumb("Results")]
    return render_template('dashboard/results.html', title='Dashboard - Results', breadcrumbs=breadcrumbs, user=current_user, results=results, filterInfo=filterInfo, valid_tags=tags)

@bp.route('/dashboard/admin')
@login_required
def admin_dashboard():
    breadcrumbs = [Breadcrumb("Admin", url_for("gui.admin_dashboard"))]
    return render_template('dashboard/admin.html', title='Dashboard - Admin', breadcrumbs=breadcrumbs, user=current_user,admin=True,filterInfo=None)