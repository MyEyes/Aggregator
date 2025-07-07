from app.models import db
from datetime import datetime
from app.models.tag import result_tags, Tag
from app.models.property import result_properties, Property, PropertyKind
from sqlalchemy.sql.expression import func, select, insert, intersect_all, intersect
import markdown

class Scan(db.Model):
    _defaultSort = "started_at"
    id = db.Column(db.Integer, primary_key=True)

    tool_id = db.Column(db.Integer, db.ForeignKey('tool.id'))
    results = db.relationship('ScanResult', backref='scan', lazy='dynamic', cascade='all')
    duplicates = db.relationship('DuplicateScanResult', backref='scan', lazy='dynamic', cascade='all, delete-orphan')
    result_tags = db.relationship('ScanResultTallies', back_populates="scan", cascade="save-update, merge, delete, delete-orphan")

    arguments = db.Column(db.Text, index=True)

    hard_match_hash = db.Column(db.String(256), index=True, unique=True)

    started_at = db.Column(db.DateTime, default = datetime.utcnow())
    finished_at = db.Column(db.DateTime, default = None)

    @classmethod
    def search(cls, val):
        search_str = "%{0}%".format(val)
        results = Scan.query
        results = results.filter(Scan.arguments.like(search_str))
        return results

    def __repr__(self):
        return f"Scan {self.id} - {self.tool.name}"

    def transfer_result_tags_to_soft_matches(self):
        raw_sql = """
        CREATE TEMPORARY TABLE soft_match_mapping (
            soft_match_hash VARCHAR(256),
            result_id INT,
            INDEX r_idx (result_id),
            INDEX s_idx (soft_match_hash)
        );

        -- Fill temp table with association of newest tag results
        INSERT INTO soft_match_mapping
        SELECT sr.soft_match_hash, nsr.id
        FROM scan_result sr
        INNER JOIN (
            SELECT soft_match_hash, max(human_touched_at) maxDate
            FROM scan_result tsr
            GROUP BY soft_match_hash
            ) MaxDates
            ON sr.soft_match_hash=MaxDates.soft_match_hash
        INNER JOIN scan_result nsr ON nsr.soft_match_hash=sr.soft_match_hash AND nsr.human_touched_at=MaxDates.maxDate
        WHERE sr.scan_id=:scan_id
        GROUP BY sr.soft_match_hash
        ORDER BY nsr.id;

        -- Wipe all tags that don't belong to a scan result in the table
        DELETE rt
        FROM result_tags rt
        JOIN scan_result sr ON sr.id=rt.result_id
        LEFT JOIN soft_match_mapping smm ON sr.id=smm.result_id
        WHERE sr.scan_id=:scan_id AND smm.result_id IS NULL;

        -- Insert tags of newest result into all soft matched results, except itself
        INSERT INTO result_tags (result_id, tag_id)
        SELECT sr.id, rt.tag_id
        FROM scan_result sr
        JOIN soft_match_mapping smm ON sr.soft_match_hash=smm.soft_match_hash
        JOIN result_tags rt ON smm.result_id=rt.result_id
        WHERE sr.scan_id=:scan_id AND sr.id!=smm.result_id;

        DROP TABLE soft_match_mapping;
        """
        db.session.execute(raw_sql, {'scan_id': self.id})
        db.session.commit()
        self.update_result_tag_tallies()

    def delete(self):
        raw_sql = """
        -- Delete all of our own duplicates
        DELETE duplicate_scan_result
        FROM duplicate_scan_result
        WHERE scan_id=:scan_id;

        -- Overwrite results scan_ids with ids of oldest duplicate results
        -- if they exist, and wipe created_at in duplicates to mark deletion
        UPDATE scan_result sr
        INNER JOIN (
                SELECT original_result_id, MIN(id) oldestId
                FROM duplicate_scan_result 
                GROUP BY original_result_id
            )
            AS oldest ON oldest.original_result_id=sr.id
        INNER JOIN duplicate_scan_result dsr ON dsr.id=oldest.oldestId
        SET sr.scan_id=dsr.scan_id,
        sr.subject_id=dsr.subject_id,
        sr.created_at=dsr.created_at,
        dsr.created_at=NULL
        WHERE sr.scan_id=:scan_id;

        -- Delete all result tags, result properties and results that still exist for this scan
        DELETE rt
        FROM scan_result sr
        JOIN result_tags rt ON sr.id=rt.result_id
        WHERE scan_id=:scan_id;

        DELETE res_prop
        FROM result_properties res_prop
        JOIN scan_result sr
        ON res_prop.result_id = sr.id
        WHERE scan_id=:scan_id;

        DELETE sr
        FROM scan_result sr
        WHERE scan_id=:scan_id;

        -- Delete all duplicate results we marked for deletion by wiping created_at
        DELETE duplicate_scan_result
        FROM duplicate_scan_result
        WHERE created_at is NULL;

        -- Delete scan
        DELETE scan
        FROM scan
        WHERE id=:scan_id;
        """
        db.session.execute(raw_sql, {'scan_id':self.id})
        db.session.commit()
        Scan.update_all_result_tag_tallies()

    @classmethod
    def update_all_result_tag_tallies(cls):
        scans = Scan.query.all()
        for scan in scans:
            scan.update_result_tag_tallies()

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

    tags = db.relationship('Tag', secondary=result_tags, backref='results')
    properties = db.relationship('Property', secondary=result_properties, backref='results', cascade='all')

    hard_match_hash = db.Column(db.String(256), index=True, unique=True)

    created_at = db.Column(db.DateTime, default = datetime.utcnow())
    human_touched_at = db.Column(db.DateTime, default=datetime.min)
    
    def get_soft_matches(self):
        # Start with all valid subject ids and filter down by intersecting with subject ids matching each property
        soft_matches_query = select(ScanResult.__table__.c.id)
        result_id = result_properties.columns["result_id"]
        property_id = result_properties.columns["property_id"]
        property_matches = []
        for property in self.properties:
            if not property.property_kind.is_matching_property:
                continue
            property_matches.append(select(result_id).where(property_id == property.id))
            
        soft_matches_query = intersect(*property_matches)
        soft_match_ids = [ent[0] for ent in db.session.execute(soft_matches_query).all()]
        return ScanResult.query.filter(ScanResult.__table__.c.id.in_(soft_match_ids))
    
    def get_matching_properties_string(self):
        return " && ".join([prop.get_matching_string() for prop in self.properties if prop.property_kind.is_matching_property])
    
    def get_property_matches_without(self, property, exclusion_set):
        excluded_ids = [elem.id for elem in exclusion_set]
        result_set = [result for result in property.results if result.id!=self.id and result.id not in excluded_ids]
        return result_set

    def try_get_soft_notes(self):
        return None

    def set_note(self, val):
        self.notes = val

    def touch(self):
        self.human_touched_at = datetime.utcnow()

    def get_note(self):
        if self.notes and len(self.notes) > 0:
            return self.notes
        # soft_notes = self.try_get_soft_notes()
        # if soft_notes:
        #     return "SOFT: \n" + soft_notes
        return ""

    def add_tag(self, tag):
        if tag in self.tags:
            return
        self.tags.append(tag)

    def add_property(self, property_val):
        if property_val in self.properties:
            return
        self.properties.append(property_val)

    def set_tags(self, tagIds):
        if not tagIds:
            return
        try:
            self.tags = Tag.query.filter(Tag.id.in_(tagIds)).all()
            db.session.add(self)
        except Exception as e: #Fall back on error
            print(e)
            self.tags.clear()
            for tid in tagIds:
                tag = db.session.query(Tag).filter(Tag.id == tid).first()
                if not tag:
                    raise Exception(f"Tag with id {tid} does not exist")
                self.add_tag(tag)
        # It's okay to not update tallies here, because this will only happen if the result isn't
        # committed to the db yet and we will recalculate then
        #self.subject._recalculateTallies()

    # New results can only be added during a scan
    # So we defer the updating of the tallies until after the full scan is done
    def add_tags(self, tagIds):
        if not tagIds:
            return
        try:
            newTags = Tag.query.filter(Tag.id.in_(tagIds)).all()
            self.tags.extend(newTags)
        except Exception as e:
            print(e)
            for tid in tagIds:
                tag = db.session.query(Tag).filter(Tag.id == tid).first()
                if not tag:
                    raise Exception(f"Tag with id {tid} does not exist")
                self.add_tag(tag)
        # It's okay to not update tallies here, because this will only happen if the result isn't
        # committed to the db yet and we will recalculate then
        # if self.subject:
        #     self.subject._recalculateTallies()

    def add_properties(self, property_val_ids):
        if not property_val_ids:
            return
        try:
            newProperties = Property.query.filter(Property.id.in_(property_val_ids)).all()
            self.properties.extend(newProperties)
        except Exception as e:
            print(e)
            for property_val_id in property_val_ids:
                property_val = db.session.query(Property).filter(Property.id == property_val_id).first()
                if not property_val:
                    raise Exception(f"Property with id {property_val_id} does not exist")
                self.add_property(property_val)


    # export: export current result tags or import newest result tags
    def transfer_tags_to_soft_matches(self, export=True):
        soft_matches = self.get_soft_matches()
        if export:
            transferTags = [tag.id for tag in self.tags]
            for match in soft_matches:
                match.set_tags(transferTags)
                match.subject._recalculateTallies()
                match.scan.update_result_tag_tallies()
        else:
            #Find newest version of this result
            #as in the one last changed by a human
            newestOne = self
            for match in soft_matches:
                if match.human_touched_at > newestOne.human_touched_at:
                    newestOne = match
            transferTags = [tag.id for tag in newestOne.tags]
            self.set_tags(transferTags)
            self.subject._recalculateTallies()
            self.scan.update_result_tag_tallies()

    @classmethod
    def transfer_soft_tags(self):
        raw_sql = """
        CREATE TEMPORARY TABLE soft_match_mapping (
            soft_match_hash VARCHAR(256),
            result_id INT,
            INDEX r_idx (result_id),
            INDEX s_idx (soft_match_hash)
        );

        -- Fill temp table with association of newest tag results
        INSERT INTO soft_match_mapping
        SELECT sr.soft_match_hash, nsr.id
        FROM scan_result sr
        INNER JOIN (
            SELECT soft_match_hash, max(human_touched_at) maxDate
            FROM scan_result tsr
            GROUP BY soft_match_hash
            ) MaxDates
            ON sr.soft_match_hash=MaxDates.soft_match_hash
        INNER JOIN scan_result nsr ON nsr.soft_match_hash=sr.soft_match_hash AND nsr.human_touched_at=MaxDates.maxDate
        GROUP BY sr.soft_match_hash
        ORDER BY nsr.id;

        -- Wipe all tags that don't belong to a scan result in the table
        DELETE rt
        FROM result_tags rt
        JOIN scan_result sr ON sr.id=rt.result_id
        LEFT JOIN soft_match_mapping smm ON sr.id=smm.result_id
        WHERE smm.result_id IS NULL;

        -- Insert tags of newest result into all soft matched results, except itself
        INSERT INTO result_tags (result_id, tag_id)
        SELECT sr.id, rt.tag_id
        FROM scan_result sr
        JOIN soft_match_mapping smm ON sr.soft_match_hash=smm.soft_match_hash
        JOIN result_tags rt ON smm.result_id=rt.result_id
        WHERE sr.id!=smm.result_id;

        DROP TABLE soft_match_mapping;
        """
        db.session.execute(raw_sql)
        db.session.commit()

    def get_markdown(self):
        return markdown.markdown(self.raw_text, extensions=['codehilite', 'fenced_code'])
    
    def get_notes_md(self):
        return markdown.markdown(self.get_note(), extensions=['codehilite', 'fenced_code'])

    # Only use this for individual deletion
    # for other cases there are much better
    # mass implementations
    def delete(self):
        oldSub = self.subject
        oldScan = self.scan

        if len(list(self.duplicates))>0:
            self._move_to_oldest_duplicate()
            return

        db.session.delete(self)
        db.session.commit()
        oldSub._recalculateTallies()
        oldScan.update_result_tag_tallies()

    def _move_to_oldest_duplicate(self):
        oldestTime = datetime.max
        oldest = None
        for dup in self.duplicates:
            if dup.created_at < oldestTime:
                oldest = dup
                oldestTime = dup.created_at
        if not oldest:
            raise Exception("Duplicates exist, but we couldn't find an oldest one, wth")
        # Instead of deleting this result, we add it to the scan and subject of the oldest duplicate
        # and remove the duplicate instead.
        # That way we don't need to update all other duplicates original_result_id
        self.scan_id = oldest.scan_id
        self.subject_id = oldest.subject_id
        self.created_at = oldest.created_at
        db.session.delete(oldest)
        db.session.commit()
        db.session.refresh(self)
        self.subject._recalculateTallies()
        self.scan.update_result_tag_tallies()

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

    created_at = db.Column(db.DateTime, default = datetime.utcnow())


class ScanResultTallies(db.Model):
    scan_id = db.Column(db.Integer, db.ForeignKey('scan.id'), primary_key=True)
    tag_id = db.Column(db.Integer, db.ForeignKey('tag.id'), primary_key=True)
    count = db.Column(db.Integer)

    scan = db.relationship("Scan", back_populates="result_tags")
    tag = db.relationship("Tag")

    def __repr__(self):
        return f"<ResultTally, ({self.tag_id, self.scan_id}) = {self.count}>"