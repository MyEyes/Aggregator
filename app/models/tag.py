from app.models import db
from datetime import datetime
import enum
from sqlalchemy import Integer, Enum

class SpecialTag(enum.Enum):
    NONE = 0
    OPEN_TAG = 1
    UNDECIDED_TAG = 2
    CONFIRMED_TAG = 3
    REJECTED_TAG = 4

subject_tags = db.Table(
    "subject_tags",
    db.Column("subject_id", db.Integer, db.ForeignKey('subject.id')),
    db.Column("tag_id", db.Integer, db.ForeignKey('tag.id'))
)

result_tags = db.Table(
    "result_tags",
    db.Column("result_id", db.Integer, db.ForeignKey('scan_result.id')),
    db.Column("tag_id", db.Integer, db.ForeignKey('tag.id'))
)

# Tags for Subjects and Results
class Tag(db.Model):
    _defaultSort = "id"
    
    id = db.Column(db.Integer, primary_key=True)
    shortname = db.Column(db.String(10))
    color = db.Column(db.String(16))
    name = db.Column(db.String(256), index=True)
    description = db.Column(db.Text())
    special = db.Column(Enum(SpecialTag))