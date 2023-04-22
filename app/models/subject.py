from app.models import db
from datetime import datetime
from app.models.scan import ScanResult

# The subject of a scan, could be a URL, an assembly or something else
class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(256), index=True)
    altNames = db.relationship('SubjectAltNames', backref='subject', lazy='dynamic')

    host = db.Column(db.String(256), index=True)
    altPaths = db.relationship('SubjectAltPaths', backref='subject', lazy='dynamic')

    results = db.relationship('ScanResult', backref='subject', lazy='dynamic')
    duplicates = db.relationship('DuplicateScanResult', backref='subject', lazy='dynamic')

    notes = db.Column(db.Text)

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

    def get_states(self):
        return {
            'open': len(list(self.results.filter_by(state='open'))),
            'undecided': len(list(self.results.filter_by(state='undecided'))),
            'confirmed': len(list(self.results.filter_by(state='confirmed'))),
            'rejected': len(list(self.results.filter_by(state='rejected')))
        }

    def get_soft_matches(self):
        subquery = db.session.query(ScanResult.soft_match_hash).filter(ScanResult.subject_id==self.id)
        query = db.session.query(ScanResult).filter(ScanResult.subject_id != self.id).filter(ScanResult.soft_match_hash.in_(subquery))
        return query

    def get_states_string(self):
        return f"{len(list(self.results.filter_by(state='open')))}O | {len(list(self.results.filter_by(state='undecided')))}U | {len(list(self.results.filter_by(state='confirmed')))}C | {len(list(self.results.filter_by(state='rejected')))}R"

    def get_soft_match_state_string(self):
        soft_matches = self.get_soft_matches()
        return f"{len(list(soft_matches.filter_by(state='open')))}O | {len(list(soft_matches.filter_by(state='undecided')))}U | {len(list(soft_matches.filter_by(state='confirmed')))}C | {len(list(soft_matches.filter_by(state='rejected')))}R"

    def set_note(self, value):
        self.notes = value

    def get_notes(self):
        if self.notes and len(self.notes)>0:
            return self.notes
        else:
            soft_note = self.try_get_soft_notes()
            if soft_note:
                return "SOFT: \n" + soft_note
            else:
                return ""
    
    def try_get_soft_notes(self):
        for soft_match in self.get_soft_matches():
            if soft_match.notes and len(soft_match.notes)>0:
                return soft_match.notes
        return None

    @classmethod
    def search(cls, val):
        search_str = "%{0}%".format(val)
        results = Subject.query
        results = results.filter(Subject.name.like(search_str))
        return results

class SubjectAltNames(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subj_id = db.Column(db.Integer, db.ForeignKey('subject.id'))
    name = db.Column(db.Text, index=True)

class SubjectAltPaths(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subj_id = db.Column(db.Integer, db.ForeignKey('subject.id'))
    path = db.Column(db.Text, index=True)