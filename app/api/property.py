from app.api import bp
from flask import jsonify, request
from app.api.auth import token_auth
from app.api.errors import bad_request
from app.models import db
from app.models.property import Property, PropertyKind
from datetime import datetime

@bp.route('/property/register_kind', methods=['POST'])
@token_auth.login_required
def register_property_kind():
    data = request.get_json() or None
    if not data:
        return bad_request("No arguments")
    if not 'name' in data:
        return bad_request("No name")
    propertyKind = PropertyKind()
    propertyKind.name = data['name']
    propertyKind.description = data.get('description', "")
    propertyKind.is_matching_property = data.get('is_matching', False)
    
    existing = PropertyKind.query.filter_by(name=propertyKind.name).first()
    if existing:
        return jsonify(
            {
                'status': 'OK',
                'msg': 'Already registered',
                'id': existing.id
            }
        )

    db.session.add(propertyKind)
    db.session.commit()
    db.session.refresh(propertyKind) #refresh so we can get the id

    return jsonify(
        {
            'status': 'OK',
            'msg': 'Registered Tag',
            'id': propertyKind.id
        }
    )

@bp.route('/property/add', methods=['POST'])
@token_auth.login_required
def register_property_value():
    data = request.get_json() or None
    if not data:
        return bad_request("No arguments")
    if not 'kind' in data:
        return bad_request("No kind")
    if not 'value' in data:
        return bad_request("No value")
    property = Property()
    property.property_kind_id = data['kind']
    property.value = data['value']

    # Check that property kind is valid:
    kind = PropertyKind.query.filter_by(id=property.property_kind_id).first()
    if not kind:
        return bad_request(f"Unknown property kind id: {property.property_kind_id}")
    # Explicitly truncate if value is too long
    # the tool side should probably convert to a hash in those cases
    # but we don't assume we know better on the aggregation side
    # and truncate instead
    warning = ""
    if len(property.value) > 256:
        property.value = property.value[:256]
        warning = ", value too long, was truncated"
    
    existing = Property.query.filter_by(value=property.value).filter_by(property_kind_id=property.property_kind_id).first()
    if existing:
        return jsonify(
            {
                'status': 'OK',
                'msg': 'Already registered'+warning,
                'id': existing.id
            }
        )

    db.session.add(property)
    db.session.commit()
    db.session.refresh(property) #refresh so we can get the id

    return jsonify(
        {
            'status': 'OK',
            'msg': 'Registered Tag'+warning,
            'id': property.id
        }
    )