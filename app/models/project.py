from marshmallow import fields, validate, validates, ValidationError
from marshmallow_sqlalchemy import auto_field, SQLAlchemySchema
from slugify import slugify
from sqlalchemy import Column, String, DateTime, Boolean
from sqlalchemy.dialects.sqlite import JSON

from app import db
from app.models.base import BaseModel
from app.utils.mixins import CRUDMixin, SerializerMixin, TimestampMixin


def generate_unique_slug(name):
    base_slug = slugify(name)[:16]
    slug = base_slug
    count = 1
    while Project.query.filter_by(slug=slug).first():
        slug = f"{base_slug}-{count}"[:16]
        count += 1
    return slug


class Project(db.Model, BaseModel, CRUDMixin, SerializerMixin, TimestampMixin):
    __tablename__ = 'projects'

    slug = Column(String(120), unique=True, nullable=False)
    name = Column(String(120), nullable=False)
    description = Column(String(255), nullable=False)
    url = Column(String(255), nullable=True)
    image = Column(String(255), nullable=True)
    tags = Column(JSON, nullable=True)
    tech_stack = Column(JSON, nullable=True)
    source_code = Column(String(255), nullable=True)
    type = Column(String(255), nullable=False)
    status = Column(String(255), nullable=False)
    featured = Column(Boolean, default=False, nullable=False)
    begin_date = Column(DateTime, nullable=False)
    completion_date = Column(DateTime, default=None, nullable=True)

    def __init__(self, **kwargs):
        if "slug" not in kwargs or not kwargs["slug"]:
            kwargs["slug"] = generate_unique_slug(kwargs.get("name", ""))
        super().__init__(**kwargs)


class ProjectSchema(SQLAlchemySchema):
    class Meta:
        model = Project
        load_instance = True  # Allows deserialization into model instances
        include_fk = True  # Include foreign keys if applicable
        sqla_session = db.session

    id = auto_field(dump_only=True)
    slug = fields.String(
        required=False,
        validate=validate.Length(max=16)
    )
    name = fields.String(
        required=True,
        validate=validate.Length(max=120)
    )
    description = fields.String(
        required=True,
        validate=validate.Length(max=255)
    )
    url = fields.String(
        validate=validate.Length(max=255)
    )
    image = fields.String(
        validate=validate.Length(max=255)
    )
    tags = fields.Raw()
    tech_stack = fields.Raw()
    source_code = fields.String(
        validate=validate.Length(max=255)
    )
    type = fields.String(
        required=True,
        validate=validate.Length(max=16)
    )
    status = fields.String(
        required=True,
        validate=validate.Length(max=16)
    )
    featured = fields.Bool(required=True)
    begin_date = fields.DateTime(required=True)
    completion_date = fields.DateTime(default=None, allow_none=True)

    created_at = auto_field(dump_only=True)
    updated_at = auto_field(dump_only=True, load_only=True)

    @validates("slug")
    def validate_slug_unique(self, value):
        project = Project.query.filter_by(slug=value).first()
        if project:
            raise ValidationError("Slug already in use.")

    @validates("status")
    def validate_status(self, value):
        if value not in ["completed", "maintained", "developing"]:
            raise ValidationError("Invalid status.")
