import re

from sqlalchemy import Column, String
from sqlalchemy.orm import validates

from app import db
from app.exception.validation_error import ValidationError
from app.models.base import BaseModel
from app.utils.mixins import CRUDMixin, SerializerMixin, TimestampMixin

name_regex = re.compile(r'^[a-zA-Z0-9_]{3,16}$')


class SocialLink(db.Model, BaseModel, CRUDMixin, SerializerMixin, TimestampMixin):
    __tablename__ = 'social_links'

    name = Column(String(16), unique=True, nullable=False)
    description = Column(String(255), nullable=False)
    url = Column(String(255), nullable=True)
    icon = Column(String(255), nullable=False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @validates("name")
    def validate_name(self, key, value):
        if not value:
            raise ValidationError("Name is required.")
        if not name_regex.match(value):
            raise ValidationError(
                "Invalid name. Must be between 3 and 16 characters, and can only contain letters, numbers, and underscores."
            )
        if SocialLink.query.filter_by(name=value).first():
            raise ValidationError("Name already in use.")
        return value

    @validates("description")
    def validate_description(self, key, value):
        if not value:
            raise ValidationError("Description is required.")
        if len(value) < 1 or len(value) > 255:
            raise ValidationError("Invalid description. Must be between 1 and 255 characters.")
        return value

    @validates("url")
    def validate_url(self, key, value):
        if value:
            if not value.startswith("http"):
                raise ValidationError("Invalid URL. Must start with 'http' or 'https'.")
        return value

    @validates("icon")
    def validate_icon(self, key, value):
        if not value:
            raise ValidationError("Icon is required.")
        if len(value) < 1 or len(value) > 255:
            raise ValidationError("Invalid icon. Must be between 1 and 255 characters.")
