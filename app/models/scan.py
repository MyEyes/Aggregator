from app.models import db
from datetime import datetime

class Scan(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    tool_id = db.Column(db.Integer, db.ForeignKey('tool.id'))
    results = db.relationship('ScanResult', backref='scan', lazy='dynamic')
    duplicates = db.relationship('DuplicateScanResult', backref='scan', lazy='dynamic')

    arguments = db.Column(db.Text, index=True)

    soft_match_hash = db.Column(db.String(256), index=True)
    hard_match_hash = db.Column(db.String(256), index=True, unique=True)

    started_at = db.Column(db.DateTime, default = datetime.utcnow)
    finished_at = db.Column(db.DateTime, default = None)

class ScanResult(db.Model):
    id = db.Column(db.Integer, primary_key = True)

    scan_id = db.Column(db.Integer, db.ForeignKey('scan.id'))
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'))

    duplicates = db.relationship('DuplicateScanResult', backref='original_result', lazy='dynamic')

    raw_text = db.Column(db.Text, index=True)
    scan_risk_text = db.Column(db.String(50))
    manual_risk_text = db.Column(db.String(50))

    soft_match_hash = db.Column(db.String(256), index=True)
    hard_match_hash = db.Column(db.String(256), index=True, unique=True)

    created_at = db.Column(db.DateTime, default = datetime.utcnow)

class DuplicateScanResult(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    scan_id = db.Column(db.Integer, db.ForeignKey('scan.id'))
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'))
    original_result_id = db.Column(db.Integer, db.ForeignKey('scan_result.id'))

    created_at = db.Column(db.DateTime, default = datetime.utcnow)