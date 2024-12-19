import re
from datetime import datetime

from slugify import slugify
from sqlalchemy import Column, String, Boolean, Table, Integer, ForeignKey, Date
from sqlalchemy.orm import relationship, validates

from app import db
from app.exception.validation_error import ValidationError
from app.models.base import BaseModel
from app.utils.mixins import CRUDMixin, SerializerMixin, TimestampMixin
from app.utils.utils import is_valid_date

name_regex = re.compile(r'^[a-zA-Z0-9_ ]{3,120}$')


def generate_unique_slug(name):
    base_slug = slugify(name)[:16]
    slug = base_slug
    count = 1
    while Project.query.filter_by(slug=slug).first():
        slug = f"{base_slug}-{count}"[:16]
        count += 1
    return slug


# Association table
projects_tags = Table(
    'projects_tags', db.Model.metadata,
    Column('project_id', Integer, ForeignKey('projects.id'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id'), primary_key=True)
)


class Project(db.Model, BaseModel, CRUDMixin, SerializerMixin, TimestampMixin):
    __tablename__ = 'projects'

    slug = Column(String(64), unique=True, nullable=False)
    name = Column(String(120), nullable=False)
    description = Column(String(255), nullable=False)
    url = Column(String(255), nullable=True)
    image_url = Column(String(255), nullable=True)
    source_code_url = Column(String(255), nullable=True)
    type = Column(String(255), nullable=False)
    status = Column(String(255), nullable=False)
    featured = Column(Boolean, default=False, nullable=False)
    begin_date = Column(Date, nullable=False)
    completion_date = Column(Date, default=None, nullable=True)

    tags = relationship(
        'Tag',
        secondary=projects_tags,
        back_populates='projects'
    )

    def __init__(self, **kwargs):
        if "slug" not in kwargs or not kwargs["slug"]:
            kwargs["slug"] = generate_unique_slug(kwargs.get("name", ""))
        super().__init__(**kwargs)

    def add_tag(self, tag):
        if tag not in self.tags:
            self.tags.append(tag)

    def remove_tag(self, tag):
        if tag not in self.tags:
            self.tags.remove(tag)

    def clear_tags(self):
        self.tags.clear()

    def dump(self):
        return self.to_dict()

    def to_dict(self, exclude=None, partial=False):
        exclude = exclude or []
        if hasattr(self, '__table__'):
            serialized_data = {
                column.name: getattr(self, column.name)
                for column in self.__table__.columns
                if column.name not in exclude
            }
            if not partial:
                # Now check for `tags` relationships and serialize them as well.
                if hasattr(self, 'tags'):
                    serialized_data['tags'] = [tag.to_dict(partial=True) for tag in self.tags]
            return serialized_data
        raise AttributeError(f"{self.__class__.__name__} does not have a __table__ attribute.")

    @validates("slug")
    def validate_slug(self, key, value):
        if not value:
            raise ValidationError(f"Slug is required. ({self.name})")
        if len(value) < 3 or len(value) > 64:
            raise ValidationError(f"Invalid slug. Must be between 3 and 64 characters. ({self.name})")
        if Project.query.filter_by(slug=value).first():
            raise ValidationError(f"Slug already in use. ({self.name})")
        return value

    @validates("name")
    def validate_name(self, key, value):
        if not value:
            raise ValidationError(f"Name is required. ({self.name})")
        if not name_regex.match(value):
            raise ValidationError(
                f"Invalid name. Must be between 3 and 120 characters, and can only contain letters, numbers, underscores, and spaces. ({self.name})")
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
            if not value.startswith("http"):
                raise ValidationError(f"Invalid URL. Must start with 'http' or 'https'. ({self.name})")
        return value

    @validates("image_url")
    def validate_image_url(self, key, value):
        if value:
            if not value.startswith("http"):
                raise ValidationError(f"Invalid image URL. Must start with 'http' or 'https'. ({self.name})")
        return value

    @validates("source_code_url")
    def validate_source_code_url(self, key, value):
        if value:
            if not value.startswith("http"):
                raise ValidationError(f"Invalid source code URL. Must start with 'http' or 'https'. ({self.name})")
        return value

    @validates("type")
    def validate_type(self, key, value):
        if not value:
            raise ValidationError(f"Type is required. ({self.name})")
        if value not in ["personal", "commission", "other"]:
            raise ValidationError(f"Invalid type. Must be one of 'personal', 'commission', or 'other'. ({self.name})")
        return value

    @validates("status")
    def validate_status(self, key, value):
        if not value:
            raise ValidationError(f"Status is required. ({self.name})")
        if value not in ["completed", "maintained", "developing"]:
            raise ValidationError(f"Invalid status. Must be one of 'completed', 'maintained', or 'developing'. ({self.name})")
        return value

    @validates("begin_date")
    def validate_begin_date(self, key, value):
        if not value:
            raise ValidationError(f"Begin date is required. ({self.name})")
        if not is_valid_date(value):
            raise ValidationError(
                f"Invalid begin date. Must be in the format YYYY-MM-DD. ({self.name})"
            )
        return datetime.strptime(value, "%Y-%m-%d").date()

    @validates("completion_date")
    def validate_completion_date(self, key, value):
        if value:
            if not is_valid_date(value):
                raise ValidationError(
                    f"Invalid completion date. Must be in the format YYYY-MM-DD. ({self.name})"
                )
            return datetime.strptime(value, "%Y-%m-%d").date()
        return None


class Tag(db.Model, BaseModel, CRUDMixin, SerializerMixin, TimestampMixin):
    __tablename__ = 'tags'

    name = Column(String(16), unique=True, nullable=False)
    is_tech = Column(Boolean, default=False, nullable=False)

    projects = relationship(
        'Project',
        secondary=projects_tags,
        back_populates='tags'
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @staticmethod
    def get_or_create(name, is_tech=False, commit=True):
        tag = Tag.query.filter_by(name=name).first()
        if not tag:
            tag = Tag(name=name, is_tech=is_tech)
            tag.save(commit=commit)
        return tag

    def dump(self):
        return self.to_dict()

    def to_dict(self, exclude=None, partial=False):
        exclude = exclude or []
        if hasattr(self, '__table__'):
            serialized_data = {
                column.name: getattr(self, column.name)
                for column in self.__table__.columns
                if column.name not in exclude
            }
            if not partial:
                # Now check for `projects` relationships and serialize them as well.
                if hasattr(self, 'projects'):
                    serialized_data['projects'] = [project.to_dict(partial=True) for project in self.projects]
            return serialized_data
        raise AttributeError(f"{self.__class__.__name__} does not have a __table__ attribute.")

    @validates("name")
    def validate_name(self, key, value):
        if not value:
            raise ValidationError(f"Name is required. ({self.name})")
        if len(value) < 1 or len(value) > 16:
            raise ValidationError(f"Invalid name. Must be between 1 and 16 characters. ({self.name})")
        if Tag.query.filter_by(name=value).first():
            raise ValidationError(f"Name already in use. ({self.name})")
        return value
