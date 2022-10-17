from app.models import db
from datetime import datetime

# A tool executing a scan
class Tool(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String, index=True)
    description =  db.Column(db.String)

    version = db.Column(db.String)
    prev_version_id = db.Column(db.Integer)
    next_version_id = db.Column(db.Integer)

    soft_match_hash = db.Column(db.String(256))
    hard_match_hash = db.Column(db.String(256), index=True, unique=True)

    created_at = db.Column(db.DateTime, default = datetime.utcnow)
    created_by_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    scans = db.relationship('Scan', backref='tool', lazy='dynamic')