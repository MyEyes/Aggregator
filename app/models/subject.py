from app.models import db
from datetime import datetime

# The subject of a scan, could be a URL, an assembly or something else
class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(256), index=True)
    altNames = db.relationship('SubjectAltNames', backref='subject', lazy='dynamic')

    host = db.Column(db.String(256), index=True)
    altPaths = db.relationship('SubjectAltPaths', backref='subject', lazy='dynamic')

    results = db.relationship('ScanResult', backref='subject', lazy='dynamic')
    duplicates = db.relationship('DuplicateScanResult', backref='subject', lazy='dynamic')

    version = db.Column(db.String(32))
    prev_version_id = db.Column(db.Integer)
    next_version_id = db.Column(db.Integer)

    soft_match_hash = db.Column(db.String(256), index=True)
    hard_match_hash = db.Column(db.String(256), index=True, unique=True)

    created_at = db.Column(db.DateTime, default = datetime.utcnow)

    def addPath(self, path):
        known = SubjectAltPaths.query.filter_by(subj_id=self.id).filter_by(path=path).first()
        if known:
            return
        altPath = SubjectAltPaths()
        altPath.path = path
        altPath.subj_id = self.id
        db.session.add(altPath)

    def addName(self, name):
        if SubjectAltNames.query.filter_by(subj_id=self.id).filter_by(name=name).first():
            return
        altName = SubjectAltNames()
        altName.name = name
        altName.subj_id = self.id
        db.session.add(altName)

    def get_states_string(self):
        return f"{len(list(self.results.filter_by(state='open')))}O | {len(list(self.results.filter_by(state='undecided')))}U | {len(list(self.results.filter_by(state='confirmed')))}C | {len(list(self.results.filter_by(state='rejected')))}R"

class SubjectAltNames(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subj_id = db.Column(db.Integer, db.ForeignKey('subject.id'))
    name = db.Column(db.Text, index=True)

class SubjectAltPaths(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subj_id = db.Column(db.Integer, db.ForeignKey('subject.id'))
    path = db.Column(db.Text, index=True)