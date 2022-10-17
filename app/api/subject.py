from app.api import bp
from flask import jsonify, request
from app.api.auth import token_auth
from app.api.errors import bad_request
from app.models import db
from app.models.scan import Scan
from app.models.tool import Tool
from app.models.subject import Subject, SubjectAltNames, SubjectAltPaths
from datetime import datetime

@bp.route('/subject/create', methods=['POST'])
@token_auth.login_required
def create_subject():
    data = request.get_json() or {}
    if 'name' not in data:
        return bad_request("Name required")
    if 'soft_hash' not in data:
        return bad_request("Soft hash required")
    if 'hash' not in data:
        return bad_request("Hash required")
    if 'host' not in data:
        return bad_request("Host required")
    if 'path' not in data:
        return bad_request("Path required")
    
    existing = Subject.query.filter_by(hard_match_hash=data['hash']).first()
    if existing:
        existing.addName(data['name'])
        existing.addPath(data['path'])
        db.session.commit()
        return jsonify(
        {
            'status': 'Success',
            'msg': 'Subject Updated'
        }
    )

    prev_ver = Subject.query.filter_by(soft_match_hash=data['soft_hash']).first()

    subject = Subject()
    subject.name = data['name']
    subject.created_at = datetime.utcnow()
    subject.hard_match_hash = data['hash']
    subject.soft_match_hash = data['soft_hash']
    subject.host = data['host']
    db.session.add(subject)

    subject.addPath(data['path'])
    if 'version' in data:
        subject.version = data['version']

    if prev_ver:
        while prev_ver.next_version_id and prev_ver.next_version_id != prev_ver.id:
            prev_ver = Subject.query.filter_by(id=prev_ver.next_version_id).first()
        prev_ver.next_version_id = subject.id
        subject.prev_version_id = prev_ver.id
        db.session.add(prev_ver)
        db.session.add(subject)
    
    db.session.commit()

    return jsonify(
        {
            'status': 'Success',
            'msg': 'Subject Created'
        }
    )