from marshmallow import fields, validate, validates, ValidationError
from marshmallow_sqlalchemy import auto_field, SQLAlchemySchema
from sqlalchemy import Column, String

from app import db
from app.models.base import BaseModel
from app.utils.mixins import CRUDMixin, SerializerMixin, TimestampMixin


class SocialLink(db.Model, BaseModel, CRUDMixin, SerializerMixin, TimestampMixin):
    __tablename__ = 'social_links'

    name = Column(String(120), unique=True, nullable=False)
    description = Column(String(255), nullable=False)
    url = Column(String(255), nullable=True)
    icon = Column(String(255), nullable=False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class SocialLinkSchema(SQLAlchemySchema):
    class Meta:
        model = SocialLink
        load_instance = True  # Allows deserialization into model instances
        include_fk = True  # Include foreign keys if applicable
        sqla_session = db.session

    id = auto_field(dump_only=True)
    name = fields.String(
        required=True,
        validate=validate.Length(max=16)
    )
    description = fields.String(
        required=True,
        validate=validate.Length(max=128)
    )
    url = fields.String(
        required=True,
        validate=validate.Length(max=255)
    )
    icon = fields.String(
        required=True,
        validate=validate.Length(max=64)
    )

    created_at = auto_field(dump_only=True)
    updated_at = auto_field(dump_only=True, load_only=True)

    @validates("name")
    def validate_name_unique(self, value):
        social_link = SocialLink.query.filter_by(name=value).first()
        if social_link:
            raise ValidationError("Name already in use.")
