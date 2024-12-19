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

    name = Column(String(16), nullable=False)
    description = Column(String(255), nullable=False)
    url = Column(String(255), nullable=True)
    icon = Column(String(255), nullable=False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @validates("name")
    def validate_name(self, key, value):
        if not value:
            raise ValidationError(f"Name is required. ({self.name})")
        if not name_regex.match(value):
            raise ValidationError(
                f"Invalid name. Must be between 3 and 16 characters, and can only contain letters, numbers, and underscores. ({self.name})"
            )
        if SocialLink.query.filter_by(name=value).first():
            raise ValidationError(f"Name already in use. ({self.name})")
        return value

    @validates("description")
    def validate_description(self, key, value):
        if not value:
            raise ValidationError(f"Description is required. ({self.name})")
        if len(value) < 1 or len(value) > 255:
            raise ValidationError(f"Invalid description. Must be between 1 and 255 characters. ({self.name})")
        return value

    @validates("url")
    def validate_url(self, key, value):
        if value:
            if not (value.startswith("http") or value.startswith("mailto:")):
                raise ValidationError(f"Invalid URL. Must start with 'http' or 'https'. ({self.name})")
        return value

    @validates("icon")
    def validate_icon(self, key, value):
        if not value:
            raise ValidationError(f"Icon is required. ({self.name})")
        if len(value) < 1 or len(value) > 255:
            raise ValidationError(f"Invalid icon. Must be between 1 and 255 characters. ({self.name})")
        return value