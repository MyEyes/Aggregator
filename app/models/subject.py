from app.models import db
from datetime import datetime
from app.models.scan import ScanResult
from app.models.tag import subject_tags, Tag, SpecialTag
from flask import current_app
import hashlib
import binascii
import threading

# The subject of a scan, could be a URL, an assembly or something else
class Subject(db.Model):
    _defaultSort = "created_at"
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(256), index=True)
    altNames = db.relationship('SubjectAltNames', backref='subject', lazy='dynamic', cascade='all, delete, delete-orphan')

    altPaths = db.relationship('SubjectAltPaths', backref='subject', lazy='dynamic', cascade='all, delete, delete-orphan')

    results = db.relationship('ScanResult', backref='subject', lazy='dynamic', cascade='all')
    duplicates = db.relationship('DuplicateScanResult', backref='subject', lazy='dynamic', cascade='all')

    tags = db.relationship('Tag', secondary=subject_tags, backref='subjects', cascade='all')
    child_tags = db.relationship('SubjectChildTallies', back_populates="subject", cascade="save-update, merge, delete, delete-orphan")
    result_tags = db.relationship('SubjectResultTallies', back_populates="subject", cascade="save-update, merge, delete, delete-orphan")

    parent = db.relationship('Subject', remote_side=[id], backref='children', cascade="all, delete")
    parentId = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=True)

    notes = db.Column(db.Text)

    version = db.Column(db.String(32))
    prev_version_id = db.Column(db.Integer)
    next_version_id = db.Column(db.Integer)

    soft_match_hash = db.Column(db.String(256), index=True)
    chained_soft_match_hash = db.Column(db.String(256), index=True)
    hard_match_hash = db.Column(db.String(256), index=True, unique=True)

    created_at = db.Column(db.DateTime, default = datetime.utcnow)
    human_touched_at = db.Column(db.DateTime, default=datetime.min)

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

    def touch(self):
        self.human_touched_at = datetime.utcnow

    def getTopParent(self):
        curr = self
        while curr.parent:
            curr = curr.parent
        return curr

    # Will check that parent exists and set parentId
    # But will not perform heavy duty updates
    def set_parent_light(self, parentId):
        if not parentId:
            self.chained_soft_match_hash = self.soft_match_hash
            #self._recalculateTallies()
            return
        parentId = int(parentId)
        if parentId < 0:
            self.chained_soft_match_hash = self.soft_match_hash
            #self._recalculateTallies()
            return
        parent = db.session.query(Subject).filter(Subject.id == parentId).first()
        if not parent:
            raise Exception(f"No subject with id {parentId} is known")
        self.parentId = parentId
        return

    def set_parent(self, parentId):
        if not parentId:
            self.chained_soft_match_hash = self.soft_match_hash
            self._recalculateTallies()
            return
        parentId = int(parentId)
        if parentId < 0:
            self.chained_soft_match_hash = self.soft_match_hash
            self._recalculateTallies()
            return
        parent = db.session.query(Subject).filter(Subject.id == parentId).first()
        if not parent:
            raise Exception(f"No subject with id {parentId} is known")
        self.parentId = parentId
        # We're doing this here so that the subject is visible as a child for parents
        db.session.add(self)
        db.session.commit()
        db.session.refresh(self)
        self._propagateSoftHashFromParent(parent)
        # This will propagate to the parent
        self._recalculateTallies()

    def _propagateSoftHashFromParent(self, parent):
        if parent == None:
            self.chained_soft_match_hash = self.soft_match_hash
        else:
            self.chained_soft_match_hash = hashlib.sha256(binascii.unhexlify(parent.chained_soft_match_hash)+binascii.unhexlify(self.soft_match_hash)).hexdigest()
        db.session.add(self)
        for c in self.children:
            c._propagateSoftHashFromParent(self)

    def _updateChildTally(self, tag_id, change):
        pass

    def _updateResultTally(self, tag_id, change):
        pass

    def _recalculateOwnTallies(self):
        childCalcDict = {}
        resultCalcDict = {}
        for r in self.results:
            # Count our own results tags too, they are technically under the subject
            for t in r.tags:
                if t.id not in resultCalcDict:
                    resultCalcDict[t.id] = 1
                else:
                    resultCalcDict[t.id] += 1
        for c in self.children:
            # Also count tags in the children themselves, just exclude our own tags
            for t in c.tags:
                if t.id not in childCalcDict:
                    childCalcDict[t.id] = 1
                else:
                    childCalcDict[t.id] += 1
            for ctt in c.child_tags:
                if ctt.tag_id not in childCalcDict:
                    childCalcDict[ctt.tag_id] = ctt.count
                else:
                    childCalcDict[ctt.tag_id] += ctt.count
            for rtt in c.result_tags:
                if rtt.tag_id not in resultCalcDict:
                    resultCalcDict[rtt.tag_id] = rtt.count
                else:
                    resultCalcDict[rtt.tag_id] += rtt.count
        
        child_tallies = []
        for tag_id,count in childCalcDict.items():
            child_tally = SubjectChildTallies()
            child_tally.tag_id = tag_id
            child_tally.subject_id = self.id
            child_tally.subject = self
            child_tally.count = count
            child_tallies.append(child_tally)
        self.child_tags = child_tallies

        result_tallies = []
        for tag_id,count in resultCalcDict.items():
            result_tally = SubjectResultTallies()
            result_tally.tag_id = tag_id
            result_tally.subject_id = self.id
            result_tally.subject = self
            result_tally.count = count
            result_tallies.append(result_tally)
        self.result_tags = result_tallies

    # Recalculate child subject and result tallies
    # We can use self.id and self.parent here because the Subject should have been committed to the db already
    def _recalculateTallies(self):
        childCalcDict = {}
        resultCalcDict = {}
        with db.session.no_autoflush:
            if not self.id:
                db.session.add(self)
                db.session.commit()
                db.session.refresh(self)
            self._recalculateOwnTallies()

            db.session.merge(self)
            db.session.commit()
            db.session.refresh(self)
        if self.parent:
            self.parent._recalculateTallies()

    # Recalculate child subject and result tallies, recursve down to leaf children first to guarantee that all children already have caches
    # This should only be called from recalculate all since no subject ids or anything should be updated in here for performance reasons
    def _recalculateTalliesRecursive(self):
        childCalcDict = {}
        resultCalcDict = {}
        # We don't want things to be flushed automatically
        # The main goal here is to speed up submission of new subjects and results, so the plan
        # is to defer the cache calculations until the end of a scan
        # The main benefit of this is that the caches are basically independent, so the
        # submitting process can terminate earlier to let another scan start while the caches are rebuilt in the background
        with db.session.no_autoflush:
            for c in self.children:
                c._recalculateTalliesRecursive()
            self._recalculateOwnTallies()

            db.session.add(self)

    @classmethod
    def _calculateCaches(cls, context):
        context.push()
        top_level_subjects = Subject.query.filter(Subject.parentId==None).all()
        for tls in top_level_subjects:
            tls._recalculateTalliesRecursive()
            tls._propagateSoftHashFromParent(None)
        db.session.commit()

    @classmethod
    def calculateCaches(cls):
        workerThread = threading.Thread(target=cls._calculateCaches, args=[current_app.app_context()])
        workerThread.daemon = True
        workerThread.start()

    @classmethod
    def _calculateScanCaches(cls, scan_id):
        top_level_subjects = Subject.query.filter_by(scan_id=scan_id).filter(Subject.parentId==None).all()
        for tls in top_level_subjects:
            tls._recalculateTalliesRecursive()
            tls._propagateSoftHashFromParent(None)
        db.session.commit()

    @classmethod
    def calculateScanCaches(cls, scan_id):
        cls._calculateScanCaches(scan_id)


    def get_soft_matches(self):
        soft_matches = Subject.query.filter_by(soft_match_hash=self.soft_match_hash).filter(Subject.id != self.id)
        return soft_matches

    def get_soft_matched_results(self):
        subquery = db.session.query(ScanResult.soft_match_hash).filter(ScanResult.subject_id==self.id)
        query = db.session.query(ScanResult).filter(ScanResult.subject_id != self.id).filter(ScanResult.soft_match_hash.in_(subquery))
        return query

    def transfer_result_tags(self, recursive=False, mass=False):
        if recursive:
            for child in self.children:
                child.transfer_result_tags(recursive, mass)
        for r in self.results:
            r.transfer_tags_to_soft_matches(force=False, mass=True)
        if not mass:
            self._recalculateTallies()


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

    def set_tags(self, tagIds, updateCache=True):
        try:
            self.tags = Tag.query.filter(Tag.id.in_(tagIds)).all()
        except Exception as e:
            #Fallback
            self.tags.clear()
            for tid in tagIds:
                tag = db.session.query(Tag).filter(Tag.id == tid).first()
                if not tag:
                    raise Exception(f"Tag with id {tid} does not exist")
                self.tags.append(tag)
        if updateCache:
            db.session.merge(self)
            self._recalculateTallies()
        else:
            db.session.add(self)

    def add_tags(self, tagIds, updateCache=True):
        try:
            newTags = Tag.query.filter(Tag.id.in_(tagIds)).all()
            self.tags.extend(newTags)
        except Exception as e:
            #Fallback
            print(e)
            for tid in tagIds:
                tag = db.session.query(Tag).filter(Tag.id == tid).first()
                if not tag:
                    raise Exception(f"Tag with id {tid} does not exist")
                if tag in self.tags:
                    continue
                self.tags.append(tag)
        if updateCache:
            db.session.merge(self)
            self._recalculateTallies()
        else:
            db.session.add(self)

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



class SubjectChildTallies(db.Model):
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), primary_key=True)
    tag_id = db.Column(db.Integer, db.ForeignKey('tag.id'), primary_key=True)
    count = db.Column(db.Integer)

    subject = db.relationship("Subject", back_populates="child_tags")
    tag = db.relationship("Tag")

    def __repr__(self):
        return f"<ChildTally, ({self.tag_id, self.subject_id}) = {self.count}>"

class SubjectResultTallies(db.Model):
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), primary_key=True)
    tag_id = db.Column(db.Integer, db.ForeignKey('tag.id'), primary_key=True)
    count = db.Column(db.Integer)

    subject = db.relationship("Subject", back_populates="result_tags")
    tag = db.relationship("Tag")

    def __repr__(self):
        return f"<ResultTally, ({self.tag_id, self.subject_id}) = {self.count}>"