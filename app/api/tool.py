from app.api import bp
from flask import jsonify, request
from app.api.auth import token_auth
from app.api.errors import bad_request
from app.models import db
from app.models.scan import Scan
from app.models.tool import Tool
from datetime import datetime

@bp.route('/tool/register', methods=['POST'])
@token_auth.login_required
def register_tool():
    data = request.get_json() or None
    if not data:
        return bad_request("No arguments")
    if not 'hard_match_hash' in data:
        return bad_request("No hard hash")
    if not 'name' in data:
        return bad_request("No name")
    user = token_auth.current_user()
    tool = Tool()
    tool.created_at = datetime.utcnow()
    tool.created_by_id = user.id
    tool.name = data['name']
    tool.hard_match_hash = data['hard_match_hash']
    tool.next_version_id = None
    if 'version' in data:
        tool.version = data['version']
    if 'description' in data:
        tool.description = data['description']
    
    existing = Tool.query.filter_by(hard_match_hash=tool.hard_match_hash).first()
    if existing:
        return jsonify(
            {
                'id': tool.id,
                'status': 'OK',
                'msg': 'Already registered'
            }
        )
    db.session.add(tool)
    prev_ver = Tool.query.filter_by(soft_match_hash=tool.soft_match_hash).first()
    if prev_ver:
        while prev_ver.next_version_id and not prev_ver.id == prev_ver.next_version_id:
            prev_ver = Tool.query.filter_by(id=prev_ver.next_version_id).first()
        prev_ver.next_version_id = tool.id
        tool.prev_version_id = prev_ver.id
        db.session.add(prev_ver)

    db.session.add(tool)
    db.session.commit()
    db.session.refresh(tool)

    return jsonify(
        {
            'id': tool.id,
            'status': 'OK',
            'msg': 'Registered Tool'
        }
    )