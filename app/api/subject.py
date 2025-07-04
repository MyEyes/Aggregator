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
    if 'hash' not in data:
        return bad_request("Hash required")

    tags = data.get('tags', [])
    properties = data.get('properties')
    parentId = data.get('parentId')
    if parentId and parentId < 0:
        parentId = None
    
    existing = Subject.query.filter_by(hard_match_hash=data['hash']).first()
    if existing:
        if existing.parentId != parentId:
            # Don't error if parent isn't set
            if existing.parentId and existing.parentId >= 0:
                return bad_request("Subject exists with different parent", "Subject exists with different parent")
            existing.parentId = parentId
        existing.addName(data['name'])
        existing.add_tags(tags, updateCache=False)
        existing.add_properties(properties)
        db.session.commit()
        return jsonify(
        {
            'status': 'Success',
            'msg': 'Subject Updated',
            'id': existing.id
        }
    )

    subject = Subject()
    subject.name = data['name']
    subject.created_at = datetime.utcnow()
    subject.hard_match_hash = data['hash']

    subject.set_parent_light(parentId)
    db.session.add(subject)
    db.session.commit()
    db.session.refresh(subject) #Make sure id is available

    subject.add_tags(tags,updateCache=False)
    subject.add_properties(properties)
    
    db.session.commit()

    return jsonify(
        {
            'status': 'Success',
            'msg': 'Subject Created',
            'id': subject.id
        }
    )