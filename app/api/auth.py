from app.api import bp
from flask import jsonify
from app.api.errors import bad_request
from app.models import db
from app.models.user import User
from datetime import datetime
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth

basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth()

@basic_auth.verify_password
def verify_password(username, password):
    user = User.query.filter_by(name=username).first()
    if user and user.check_password(password):
        return user

@basic_auth.error_handler
def basic_auth_error(status):
    return bad_request(str(status), "Unauthorized")

@token_auth.verify_token
def verify_token(token):
    return User.check_token(token) if token else None

@token_auth.error_handler
def token_auth_error(status):
    return bad_request(str(status), "Invalid Token")

@bp.route('/auth/tokens', methods=['POST'])
@basic_auth.login_required
def get_token():
    token = basic_auth.current_user().get_token()
    db.session.commit()
    return jsonify({'status': 'OK', 'token': token})

@bp.route('/auth/tokens', methods=['DELETE'])
@token_auth.login_required
def revoke_token():
    token_auth().current_user().revoke_token()
    db.session.commit()
    return jsonify({'status': 'OK', 'token': None})