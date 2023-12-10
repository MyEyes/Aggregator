from app.gui import bp
from flask import render_template, request, redirect, url_for
from flask_login import current_user, login_required
from app.models.scan import Scan, ScanResult
from app.models.subject import Subject
from app.models.tool import Tool
from sqlalchemy import desc, asc

@bp.route('/scan/<int:id>')
@login_required
def scan(id):
    scan = Scan.query.filter_by(id=id).first()
    results = ScanResult.query.filter_by(scan_id=scan.id)
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
    return render_template('scan/scan.html', title=str(scan), user=current_user, scan=scan, results=results, sort=_sort, sort_op=_sort_op)

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