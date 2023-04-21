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

    @classmethod
    def search(cls, val):
        search_str = "%{0}%".format(val)
        results = Scan.query
        results = results.filter(Scan.arguments.like(search_str))
        return results

    def __repr__(self):
        return f"Scan {self.id} - {self.tool.name}"

    def get_soft_matches(self):
        subquery = db.session.query(ScanResult.soft_match_hash).filter(ScanResult.scan_id==self.id)
        query = db.session.query(ScanResult).filter(ScanResult.scan_id != self.id).filter(ScanResult.soft_match_hash.in_(subquery))
        return query

    def get_states(self):
        return {
            'open': len(list(self.results.filter_by(state='open'))),
            'undecided': len(list(self.results.filter_by(state='undecided'))),
            'confirmed': len(list(self.results.filter_by(state='confirmed'))),
            'rejected': len(list(self.results.filter_by(state='rejected')))
        }

    def get_states_string(self):
        return f"{len(list(self.results.filter_by(state='open')))}O | {len(list(self.results.filter_by(state='undecided')))}U | {len(list(self.results.filter_by(state='confirmed')))}C | {len(list(self.results.filter_by(state='rejected')))}R"
    
    def get_soft_match_state_string(self):
        soft_matches = self.get_soft_matches()
        return f"{len(list(soft_matches.filter_by(state='open')))}O | {len(list(soft_matches.filter_by(state='undecided')))}U | {len(list(soft_matches.filter_by(state='confirmed')))}C | {len(list(soft_matches.filter_by(state='rejected')))}R"

class ScanResult(db.Model):
    id = db.Column(db.Integer, primary_key = True)

    scan_id = db.Column(db.Integer, db.ForeignKey('scan.id'))
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'))

    duplicates = db.relationship('DuplicateScanResult', backref='original_result', lazy='dynamic')

    raw_text = db.Column(db.Text, index=True)
    scan_risk_text = db.Column(db.String(50))
    manual_risk_text = db.Column(db.String(50))
    notes = db.Column(db.Text)

    state = db.Column(db.String(32), index=True, default="open")

    soft_match_hash = db.Column(db.String(256), index=True)
    hard_match_hash = db.Column(db.String(256), index=True, unique=True)

    created_at = db.Column(db.DateTime, default = datetime.utcnow)

    def set_state(self, new_state):
        valid_states = ["open","confirmed","rejected","undecided"]
        if new_state in valid_states:
            self.state = new_state

    def get_soft_matches(self):
        query = db.session.query(ScanResult).filter(ScanResult.soft_match_hash == self.soft_match_hash)
        return query

    def try_get_soft_notes(self):
        for soft_match in self.get_soft_matches():
            if soft_match.notes and len(soft_match.notes)>0:
                return soft_match.notes
        return ""

    def set_note(self, val):
        self.notes = val

    def get_note(self):
        if self.notes and len(self.notes) > 0:
            return self.notes
        return self.try_get_soft_notes()

    @classmethod
    def search(cls, val):
        search_str = "%{0}%".format(val)
        results = ScanResult.query
        results = results.filter(ScanResult.raw_text.like(search_str))
        return results

class DuplicateScanResult(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    scan_id = db.Column(db.Integer, db.ForeignKey('scan.id'))
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'))
    original_result_id = db.Column(db.Integer, db.ForeignKey('scan_result.id'))

    created_at = db.Column(db.DateTime, default = datetime.utcnow)