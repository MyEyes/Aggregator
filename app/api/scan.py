from app.api import bp
from flask import jsonify, request
from app.api.auth import token_auth
from app.api.errors import bad_request
from app.models import db
from app.models.scan import Scan, ScanResult, DuplicateScanResult
from app.models.tool import Tool
from app.models.subject import Subject
from datetime import datetime

@bp.route('/scan/start', methods=['POST'])
@token_auth.login_required
def start_scan():
    data = request.get_json() or {}

    tool = None
    if 'tool_hash' in data:
        tool = Tool.query.filter_by(hard_match_hash=data['tool_hash']).first()
    if not tool and 'tool_soft_hash' in data:
        tool = Tool.query.filter_by(soft_match_hash=data['tool_soft_hash']).first()
    if not tool and 'tool_name' in data :
        tool = Tool.query.filter_by(name=data['tool_name']).first()
    if not tool:
        return bad_request('Must specify valid tool')

    if not 'scan_hash' in data:
        return bad_request('Must specify scan hash')
    elif Scan.query.filter_by(hard_match_hash=data['scan_hash']).first():
        return bad_request('Scan already exists')

    if not 'scan_soft_hash' in data:
        return bad_request('Must specify scan soft hash')

    scan = Scan()
    if 'arguments' in data:
        scan.arguments = data['arguments']
    scan.tool_id = tool.id
    scan.hard_match_hash = data['scan_hash']
    scan.soft_match_hash = data['scan_soft_hash']
    scan.started_at = datetime.utcnow()
    scan.finished_at = None

    db.session.add(scan)
    db.session.commit()
    return jsonify(
        {
            'status': 'OK',
            'msg': 'Scan Created'
        }
    )

@bp.route('/scan/stop', methods=['POST'])
@token_auth.login_required
def stop_scan():
    data = request.get_json() or {}
    if not 'scan_hash' in data:
        return bad_request("Need to specify scan hash")
    scan = Scan.query.filter_by(hard_match_hash=data['scan_hash']).first()
    if not scan:
        return bad_request("No such scan")
    if scan.finished_at:
        return bad_request("Scan already finished")
    scan.finished_at = datetime.utcnow()
    db.session.add(scan)
    db.session.commit()
    return jsonify(
        {
            'status': 'OK',
            'msg': 'Scan Marked Finished'
        }
    )

@bp.route('/scan/submit', methods=['POST'])
@token_auth.login_required
def submit_scan_result():
    data = request.get_json() or {}
    if not 'scan_hash' in data:
        return bad_request("Need to specify scan hash")
    scan = Scan.query.filter_by(hard_match_hash=data['scan_hash']).first()
    if not scan:
        return bad_request("No such scan")
    if not 'subject_hash' in data:
        return bad_request("Need to specify subject hash")
    subject = Subject.query.filter_by(hard_match_hash=data['subject_hash']).first()
    if not subject:
        return bad_request("No such subject")
    if 'hash' not in data:
        return bad_request("Need to specify result hash")
    if 'soft_hash' not in data:
        return bad_request("Need to specify result soft hash")
    if 'risk' not in data:
        return bad_request("Need to specify result risk")
    if 'description' not in data:
        return bad_request("Need to specify result description")
    if 'title' not in data:
        return bad_request("Need to specify result title")
    
    existing = ScanResult.query.filter_by(hard_match_hash=data['hash']).first()
    if existing:
        duplicateResult = DuplicateScanResult()
        duplicateResult.original_result_id = existing.id
        duplicateResult.subject_id = subject.id
        duplicateResult.scan_id = scan.id
        db.session.add(duplicateResult)
        db.session.commit()
        return jsonify(
        {
        'status': 'OK',
        'msg': 'Duplicate scan result submitted'
        })

    soft_existing = ScanResult.query.filter_by(soft_match_hash=data['soft_hash']).first()
    if soft_existing:
        #TODO handle soft match case
        pass

    scanResult = ScanResult()
    scanResult.hard_match_hash = data['hash']
    scanResult.soft_match_hash = data['soft_hash']
    scanResult.scan_risk_text = data['risk']
    scanResult.subject_id = subject.id
    scanResult.scan_id = scan.id
    scanResult.title = data['title']
    scanResult.raw_text = data['description']
    scanResult.set_tags(data.get('tags'))

    db.session.add(scanResult)
    db.session.commit()
    
    return jsonify(
        {
        'status': 'OK',
        'msg': 'Scan result submitted'
        })