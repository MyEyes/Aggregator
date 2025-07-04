from app.api import bp
from flask import jsonify, request
from app.api.auth import token_auth
from app.api.errors import bad_request
from app.models import db
from app.models.tag import Tag
from datetime import datetime

@bp.route('/tag/register', methods=['POST'])
@token_auth.login_required
def register_tag():
    data = request.get_json() or None
    if not data:
        return bad_request("No arguments")
    if not 'shortname' in data:
        return bad_request("No shortname")
    if not 'name' in data:
        return bad_request("No name")
    if not 'color' in data:
        return bad_request("No color")
    special = data.get('special')
    tag = Tag()
    tag.name = data['name']
    tag.color = data['color']
    tag.shortname = data['shortname']
    #Truncate shortname if too long
    if len(tag.shortname)>Tag.SHORTNAME_MAX_LEN:
        tag.shortname = tag.shortname[:Tag.SHORTNAME_MAX_LEN]
    tag.description = data.get('description')
    
    existing = Tag.query.filter_by(name=tag.name).first()
    if existing:
        if special:
            existing.special = special
        return jsonify(
            {
                'status': 'OK',
                'msg': 'Already registered',
                'id': existing.id
            }
        )

    db.session.add(tag)
    db.session.commit()
    db.session.refresh(tag) #refresh so we can get the id

    return jsonify(
        {
            'status': 'OK',
            'msg': 'Registered Tag',
            'id': tag.id
        }
    )