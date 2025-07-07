from app.models import db
from datetime import datetime
from app.models.scan import ScanResult
from app.models.tag import subject_tags, Tag
from app.models.property import subject_properties, Property, PropertyKind
from flask import current_app
from sqlalchemy.orm import load_only
from sqlalchemy import intersect, intersect_all, select
import hashlib
import binascii
import threading
import markdown

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
    properties = db.relationship('Property', secondary=subject_properties, backref='subjects', cascade='all')
    child_tags = db.relationship('SubjectChildTallies', back_populates="subject", cascade="save-update, merge, delete, delete-orphan")
    result_tags = db.relationship('SubjectResultTallies', back_populates="subject", cascade="save-update, merge, delete, delete-orphan")

    parent = db.relationship('Subject', remote_side=[id], backref='children', cascade="all, delete")
    parentId = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=True)

    depth = db.Column(db.Integer, default=0)

    notes = db.Column(db.Text)

    version = db.Column(db.String(32))
    prev_version_id = db.Column(db.Integer)
    next_version_id = db.Column(db.Integer)

    hard_match_hash = db.Column(db.String(256), index=True, unique=True)

    created_at = db.Column(db.DateTime, default = datetime.utcnow())
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
        self.human_touched_at = datetime.utcnow()

    def getTopParent(self):
        curr = self
        while curr.parent:
            curr = curr.parent
        return curr

    # Will check that parent exists and set parentId
    # But will not perform heavy duty updates
    def set_parent_light(self, parentId):
        if not parentId:
            #self._recalculateTallies()
            return
        parentId = int(parentId)
        if parentId < 0:
            #self._recalculateTallies()
            return
        # Check if parent exists and load depth as well
        parent = db.session.query(Subject).filter(Subject.id == parentId).options(load_only("id","depth")).first()
        if not parent:
            raise Exception(f"No subject with id {parentId} is known")
        self.parentId = parentId
        self.depth = parent.depth+1
        return

    def set_parent(self, parentId):
        if not parentId:
            self._recalculateTallies()
            return
        parentId = int(parentId)
        if parentId < 0:
            self._recalculateTallies()
            return
        parent = db.session.query(Subject).filter(Subject.id == parentId).options(load_only("id","depth")).first()
        if not parent:
            raise Exception(f"No subject with id {parentId} is known")
        self.parentId = parentId
        self.depth=parent.depth+1
        # We're doing this here so that the subject is visible as a child for parents
        db.session.add(self)
        db.session.commit()
        db.session.refresh(self)
        # This will propagate to the parent
        self._recalculateTallies()

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

    #Deprecated
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
        cls.tallyAllDepths()

    @classmethod
    def _calculateScanCaches(cls, scan_id):
        cls.tallyAllDepths()
        db.session.commit()

    @classmethod
    def calculateScanCaches(cls, scan_id):
        # Just recalculates all tallies
        cls.tallyAllDepths()
        #cls._calculateScanCaches(scan_id)


    # Way faster method to tally child and result tags
    @classmethod
    def tallyAllDepths(cls):
        # Find max depth
        raw_sql = """SELECT max(depth) from subject;"""
        max_depth = db.session.execute(raw_sql).one()[0]
        # Wipe all tallies
        raw_sql = """DELETE FROM subject_child_tallies;"""
        db.session.execute(raw_sql)
        raw_sql = """DELETE FROM subject_result_tallies;"""
        db.session.execute(raw_sql)
        for depth in range(max_depth, -1, -1):
            cls._tallyAtDepth(depth)
        db.session.commit()


    @classmethod
    def _tallyAtDepth(cls, depth):
        # We assume that the tally tables have all been emptied
        # First we count all the tags on results

        raw_sql = """
        INSERT INTO subject_result_tallies (subject_id, tag_id, count)
        SELECT subject.id, result_tags.tag_id, COUNT(*)
        FROM subject
        JOIN scan_result ON scan_result.subject_id=subject.id
        JOIN result_tags ON result_id=scan_result.id
        WHERE subject.depth=:depth
        GROUP BY subject_id, tag_id;
        """
        db.session.execute(raw_sql, {'depth': depth})

        # Then we sum up all of the tallies of children of subjects at the current depth
        raw_sql = """
        INSERT INTO subject_result_tallies (subject_id, tag_id, count)
        SELECT subject.id, srt.tag_id , SUM(srt.count)
        FROM subject JOIN subject child ON child.parentId=subject.id
        JOIN subject_result_tallies srt ON subject_id=child.id
        WHERE subject.depth=:depth
        GROUP BY subject.id, srt.tag_id
        ON DUPLICATE KEY UPDATE count=count+VALUES(count);
        """
        db.session.execute(raw_sql, {'depth': depth})

        # We do basically the same thing for the subject child tags
        # Count tags on child subjects
        raw_sql = """
        INSERT INTO subject_child_tallies (subject_id, tag_id, count)
        SELECT subject.id, subject_tags.tag_id, COUNT(*)
        FROM subject
        JOIN subject child ON child.parentId=subject.id
        JOIN subject_tags ON subject_id=child.id
        WHERE subject.depth=:depth
        GROUP BY subject.id, tag_id;
        """
        db.session.execute(raw_sql, {'depth': depth})

        # Add tallies of child subjects
        raw_sql = """
        INSERT INTO subject_child_tallies (subject_id, tag_id, count)
        SELECT subject.id, sct.tag_id , SUM(sct.count)
        FROM subject JOIN subject child ON child.parentId=subject.id
        JOIN subject_child_tallies sct ON subject_id=child.id
        WHERE subject.depth=:depth
        GROUP BY subject.id, sct.tag_id
        ON DUPLICATE KEY UPDATE count=count+VALUES(count);
        """
        db.session.execute(raw_sql, {'depth': depth})


    def get_soft_matches(self):
        # Start with all valid subject ids and filter down by intersecting with subject ids matching each property
        soft_matches_query = select(Subject.__table__.c.id)
        subject_id = subject_properties.columns["subject_id"]
        property_id = subject_properties.columns["property_id"]
        property_matches = []
        for property in self.properties:
            if not property.property_kind.is_matching_property:
                continue
            property_matches.append(select(subject_id).where(property_id == property.id))
            
        soft_matches_query = intersect(*property_matches)
        soft_match_ids = [ent[0] for ent in db.session.execute(soft_matches_query).all()]
        return Subject.query.filter(Subject.__table__.c.id.in_(soft_match_ids))
    
    def get_matching_properties_string(self):
        return " && ".join([prop.get_matching_string() for prop in self.properties if prop.property_kind.is_matching_property])
    
    def get_property_matches_without(self, property, exclusion_set):
        excluded_ids = [elem.id for elem in exclusion_set]
        return [sub for sub in property.subjects if sub.id!=self.id and sub.id not in excluded_ids]

    def transfer_result_tags(self, recursive=False, mass=False):
        if recursive:
            for child in self.children:
                child.transfer_result_tags(recursive, mass)
        for r in self.results:
            r.transfer_tags_to_soft_matches(force=False, mass=True)
        if not mass:
            self._recalculateTallies()

    # Returning the longest ones first prevents weird shifting in tables when other properties are hidden in the interface
    # when only showing the first one for example
    def get_properties_lengthwise(self):
        self.properties.sort(key=lambda prop: len(prop.value), reverse=True)
        return self.properties

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
            
    def get_notes_md(self):
        return markdown.markdown(self.get_notes(), extensions=['codehilite', 'fenced_code'])
    
    def try_get_soft_notes(self):
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

    def add_properties(self, property_val_ids):
        try:
            newPropertyVals = Property.query.filter(Property.id.in_(property_val_ids)).all()
            self.properties.extend(newPropertyVals)
        except Exception as e:
            print(e)
            for property_val_id in property_val_ids:
                property_val = db.session.query(Property).filter(Property.id == property_val_id).first()
                if not property_val:
                    raise Exception(f"Property with id {property_val_id} does not exist")
                if property_val in self.properties:
                    continue
                self.properties.append(property_val)
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