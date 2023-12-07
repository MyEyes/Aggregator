from app.models import db
from datetime import datetime
from app.models.tag import result_tags, Tag, SpecialTag
from sqlalchemy.sql.expression import func, select
import markdown

class Scan(db.Model):
    _defaultSort = "started_at"
    id = db.Column(db.Integer, primary_key=True)

    tool_id = db.Column(db.Integer, db.ForeignKey('tool.id'))
    results = db.relationship('ScanResult', backref='scan', lazy='dynamic', cascade='all')
    duplicates = db.relationship('DuplicateScanResult', backref='scan', lazy='dynamic', cascade='all, delete-orphan')
    result_tags = db.relationship('ScanResultTallies', back_populates="scan", cascade="save-update, merge, delete, delete-orphan")

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

    def update_result_tag_tallies(self):
        raw_sql = """
        SELECT tag_id, tag.shortname, tag.color, count(*) FROM scan
            JOIN scan_result ON scan_id=scan.id
            JOIN result_tags ON result_id=scan_result.id
            JOIN tag on tag_id=tag.id
            WHERE scan.id=:si GROUP BY tag_id;
        """
        result_tag_tallies = db.session.execute(raw_sql, {'si': self.id})
        self.result_tags = []
        for tally in result_tag_tallies:
            newTag = ScanResultTallies()
            newTag.scan_id = self.id
            newTag.scan = self
            newTag.tag_id = tally[0]
            newTag.count = tally[3]
            self.result_tags.append(newTag)
        db.session.add(self)
        db.session.commit()
        db.session.refresh(self)
        return self.result_tags

    def get_result_tag_tallies(self):
        if len(self.result_tags) == 0:
            return self.update_result_tag_tallies()
        return self.result_tags

    def get_states_string(self):
        return ""
    
    def get_soft_match_state_string(self):
        return ""

class ScanResult(db.Model):
    _defaultSort = "created_at"
    id = db.Column(db.Integer, primary_key = True)

    scan_id = db.Column(db.Integer, db.ForeignKey('scan.id'))
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'))

    duplicates = db.relationship('DuplicateScanResult', backref='original_result', lazy='dynamic', cascade='all, delete-orphan')

    title = db.Column(db.String(128))
    raw_text = db.Column(db.Text, index=True)
    notes = db.Column(db.Text)

    tags = db.relationship('Tag', secondary=result_tags, backref='results', cascade='all')

    soft_match_hash = db.Column(db.String(256), index=True)
    hard_match_hash = db.Column(db.String(256), index=True, unique=True)

    created_at = db.Column(db.DateTime, default = datetime.utcnow)

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
        soft_notes = self.try_get_soft_notes()
        if soft_notes:
            return "SOFT: \n" + soft_notes
        return ""

    def add_tag(self, tag):
        if tag in self.tags:
            return
        self.tags.append(tag)

    def set_tags(self, tagIds):
        if not tagIds:
            return
        self.tags.clear()
        for tid in tagIds:
            tag = db.session.query(Tag).filter(Tag.id == tid).first()
            if not tag:
                raise Exception(f"Tag with id {tid} does not exist")
            self.add_tag(tag)
        # It's okay to not update tallies here, because this will only happen if the result isn't
        # committed to the db yet and we will recalculate then
            self.subject._recalculateTallies()

    def add_tags(self, tagIds):
        if not tagIds:
            return
        for tid in tagIds:
            tag = db.session.query(Tag).filter(Tag.id == tid).first()
            if not tag:
                raise Exception(f"Tag with id {tid} does not exist")
            self.add_tag(tag)
        # It's okay to not update tallies here, because this will only happen if the result isn't
        # committed to the db yet and we will recalculate then
        if self.subject:
            self.subject._recalculateTallies()

    def get_markdown(self):
        return markdown.markdown(self.raw_text, extensions=['codehilite', 'fenced_code'])

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


class ScanResultTallies(db.Model):
    scan_id = db.Column(db.Integer, db.ForeignKey('scan.id'), primary_key=True)
    tag_id = db.Column(db.Integer, db.ForeignKey('tag.id'), primary_key=True)
    count = db.Column(db.Integer)

    scan = db.relationship("Scan", back_populates="result_tags")
    tag = db.relationship("Tag")

    def __repr__(self):
        return f"<ResultTally, ({self.tag_id, self.scan_id}) = {self.count}>"