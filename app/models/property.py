from app.models import db
from datetime import datetime

subject_properties = db.Table(
    "subject_properties",
    db.Column("subject_id", db.Integer, db.ForeignKey('subject.id'), index=True),
    db.Column("property_id", db.Integer, db.ForeignKey('property.id'), index=True)
)

db.Index('subject_property_idx', subject_properties.columns['subject_id'], subject_properties.columns['property_id'])

result_properties = db.Table(
    "result_properties",
    db.Column("result_id", db.Integer, db.ForeignKey('scan_result.id'), index=True),
    db.Column("property_id", db.Integer, db.ForeignKey('property.id'), index=True)
)

db.Index('result_property_idx', result_properties.columns['result_id'], result_properties.columns['property_id'])

class PropertyKind(db.Model):
    """
    Describes a kind of property.
    "FunctionSignature", "Path", etc.
    """
    _defaultSort = "id"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), index=True)
    description = db.Column(db.Text())
    is_matching_property = db.Column(db.Boolean)

class Property(db.Model):
    """
    Describes a specific value of a property.
    Associated with a property kind.
    """
    _defaultSort = "created_at"
    id = db.Column(db.Integer, primary_key=True)
    property_kind_id = db.Column(db.Integer, db.ForeignKey('property_kind.id'), index=True)
    property_kind = db.relationship('PropertyKind', backref='values')
    value = db.Column(db.String(256), index=True)

    def __repr__(self):
        return f"<Property {self.property_kind.name}={self.value}"
    
    def get_matching_string(self):
        return f"{self.property_kind.name} = \"{self.value}\""