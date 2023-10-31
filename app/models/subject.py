from app.models import db
from datetime import datetime
from app.models.scan import ScanResult
from app.models.tag import subject_tags, Tag, SpecialTag
import hashlib
import binascii

# The subject of a scan, could be a URL, an assembly or something else
class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(256), index=True)
    altNames = db.relationship('SubjectAltNames', backref='subject', lazy='dynamic', cascade='all, delete-orphan')

    altPaths = db.relationship('SubjectAltPaths', backref='subject', lazy='dynamic', cascade='all, delete-orphan')

    results = db.relationship('ScanResult', backref='subject', lazy='dynamic', cascade='all')
    duplicates = db.relationship('DuplicateScanResult', backref='subject', lazy='dynamic', cascade='all')

    tags = db.relationship('Tag', secondary=subject_tags, backref='subjects', cascade='all')

    parent = db.relationship('Subject', remote_side=[id], backref='children')
    parentId = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=True)

    notes = db.Column(db.Text)

    version = db.Column(db.String(32))
    prev_version_id = db.Column(db.Integer)
    next_version_id = db.Column(db.Integer)

    soft_match_hash = db.Column(db.String(256), index=True)
    chained_soft_match_hash = db.Column(db.String(256), index=True)
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

    def set_parent(self, parentId):
        if not parentId:
            self.chained_soft_match_hash = self.soft_match_hash
            return
        parentId = int(parentId)
        if parentId < 0:
            self.chained_soft_match_hash = self.soft_match_hash
            return
        parent = db.session.query(Subject).filter(Subject.id == parentId).first()
        if not parent:
            raise Exception(f"No subject with id {parentId} is known")
        self.parentId = parentId
        self._propagateSoftHashFromParent(parent)

    def _propagateSoftHashFromParent(self, parent):
        self.chained_soft_match_hash = hashlib.sha256(binascii.unhexlify(parent.chained_soft_match_hash)+binascii.unhexlify(self.soft_match_hash)).hexdigest()
        db.session.add(self)
        for c in self.children:
            c._propagateSoftHashFromParent(self)

    def get_states(self):
        return {
            'open': len(list(self.results.filter_by(state='open'))),
            'undecided': len(list(self.results.filter_by(state='undecided'))),
            'confirmed': len(list(self.results.filter_by(state='confirmed'))),
            'rejected': len(list(self.results.filter_by(state='rejected')))
        }

    def get_soft_matches(self):
        soft_matches = Subject.query.filter_by(soft_match_hash=self.soft_match_hash).filter(Subject.id != self.id)
        return soft_matches

    def get_soft_matched_results(self):
        subquery = db.session.query(ScanResult.soft_match_hash).filter(ScanResult.subject_id==self.id)
        query = db.session.query(ScanResult).filter(ScanResult.subject_id != self.id).filter(ScanResult.soft_match_hash.in_(subquery))
        return query

    def get_states_string(self):
        return f"{len(list(self.results.filter_by(state='open')))}O | {len(list(self.results.filter_by(state='undecided')))}U | {len(list(self.results.filter_by(state='confirmed')))}C | {len(list(self.results.filter_by(state='rejected')))}R"

    def get_soft_match_state_string(self):
        soft_matches = self.get_soft_matched_results()
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
        for soft_match in self.get_soft_matched_results():
            if soft_match.notes and len(soft_match.notes)>0:
                return soft_match.notes
        return None

    def set_tags(self, tagIds):
        self.tags.clear()
        for tid in tagIds:
            tag = db.session.query(Tag).filter(Tag.id == tid).first()
            if not tag:
                raise Exception(f"Tag with id {tid} does not exist")
            self.tags.append(tag)

    def add_tags(self, tagIds):
        for tid in tagIds:
            tag = db.session.query(Tag).filter(Tag.id == tid).first()
            if not tag:
                raise Exception(f"Tag with id {tid} does not exist")
            if tag in self.tags:
                continue
            self.tags.append(tag)

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