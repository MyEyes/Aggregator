from app.gui import bp
from flask import render_template, request, redirect, url_for
from flask_login import current_user, login_required
from app.models.scan import Scan, ScanResult
from app.models.subject import Subject
from app.models.tool import Tool
from sqlalchemy import desc, asc

@bp.route('/')
@bp.route('/dashboard')
@login_required
def dashboard():
    return redirect(url_for('gui.scans_dashboard'))

@bp.route('/dashboard/scans')
@login_required
def scans_dashboard():
    scans = Scan.query
    _search = None
    if "search" in request.args:
        _search = request.args["search"]
        scans = Scan.search(_search)
    _filter = None
    _filter_by = None
    if "filter" in request.args:
        _filter = request.args["filter"]
        if "filter_by" in request.args:
            _filter_by = request.args['filter_by']
            scans = scans.filter(ScanResult.__dict__[request.args['filter_by']] == request.args["filter"])
    _sort_op = "desc"
    if "sort_op" in request.args:
        _sort_op = request.args["sort_op"]
    _sort = "created_at"
    if "sort" in request.args:
        _sort = request.args['sort']
        __sort = _sort
        if _sort_op == "asc":
            scans = scans.order_by(asc(__sort))
        else:
            scans = scans.order_by(desc(__sort))
    _page = 1
    if "page" in request.args:
        _page = int(request.args['page'])
    scans = scans.paginate(page=_page, per_page=20, error_out=False)
    return render_template('dashboard/scans.html', title='Dashboard - Scans', user=current_user, scans=scans, filter=_filter, filter_by=_filter_by, sort=_sort, sort_op=_sort_op, page=_page, search=_search)

@bp.route('/dashboard/subjects')
@login_required
def subjects_dashboard():
    subjects = Subject.query
    _search = None
    if "search" in request.args:
        _search = request.args["search"]
        subjects = Subject.search(_search)
    _page = 1
    if "page" in request.args:
        _page = int(request.args['page'])
    subjects = subjects.paginate(page=_page, per_page=20, error_out=False)
    return render_template('dashboard/subjects.html', title='Dashboard - Subjects', user=current_user, subjects = subjects, page=_page, search=_search)

@bp.route('/dashboard/tools')
@login_required
def tools_dashboard():
    tools = Tool.query
    _page = 1
    if "page" in request.args:
        _page = int(request.args['page'])
    tools = tools.paginate(page=_page, per_page=20, error_out=False)
    return render_template('dashboard/tools.html', title='Dashboard - Tools', user=current_user, tools=tools, page=_page)

@bp.route('/dashboard/results')
@login_required
def results_dashboard():
    results = ScanResult.query
    _search = None
    if "search" in request.args:
        _search = request.args["search"]
        results = ScanResult.search(_search)
    _filter = None
    _filter_by = None
    if "filter" in request.args:
        _filter = request.args["filter"]
        if "filter_by" in request.args:
            _filter_by = request.args['filter_by']
            results = results.filter(ScanResult.__dict__[request.args['filter_by']] == request.args["filter"])
    _sort_op = "desc"
    if "sort_op" in request.args:
        _sort_op = request.args["sort_op"]
    _sort = "created_at"
    if "sort" in request.args:
        _sort = request.args['sort']
        __sort = _sort
        if _sort == "subject":
            results = results.join(ScanResult.subject)
            __sort = "name"
        if _sort_op == "asc":
            results = results.order_by(asc(__sort))
        else:
            results = results.order_by(desc(__sort))
    _page = 1
    if "page" in request.args:
        _page = int(request.args['page'])
    results = results.paginate(page=_page, per_page=20, error_out=False)

    return render_template('dashboard/results.html', title='Dashboard - Results', user=current_user, results=results, filter=_filter, filter_by=_filter_by, sort=_sort, sort_op=_sort_op, page=_page, search=_search)