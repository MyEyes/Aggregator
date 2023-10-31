from app.models import db, login
from datetime import datetime, timedelta
from random import randbytes
from binascii import hexlify
from flask_login import UserMixin
import hashlib

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key = True)

    name = db.Column(db.String(64), unique = True)
    pass_hash = db.Column(db.String(256))

    tokens = db.relationship('UserApiToken', backref='user', lazy='dynamic', cascade='all, delete-orphan')

    def check_password(self, passw):
        h = hashlib.sha256(passw.encode())
        if h.hexdigest() == self.pass_hash:
            return True
        return False

    def set_password(self, passw):
        h = hashlib.sha256(passw.encode())
        self.pass_hash = h.hexdigest()

    def get_token(self):
        token = UserApiToken(self.id, timedelta(minutes=20))
        db.session.add(token)
        return token.token

    @staticmethod
    def check_token(token):
        userToken = UserApiToken.query.filter_by(token=token).first()
        if userToken is None or userToken.valid_until < datetime.utcnow():
            return None
        return userToken.user

@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class UserApiToken(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    token = db.Column(db.String(256), unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    created_at = db.Column(db.DateTime, default = datetime.utcnow)
    valid_until = db.Column(db.DateTime, default = datetime.utcnow)

    def __init__(self, uid, valid_time):
        self.user_id = uid
        tok = hexlify(randbytes(128)).decode()
        self.token = tok
        self.created_at = datetime.utcnow()
        self.valid_until = self.created_at+valid_time