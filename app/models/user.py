import re

import email_validator
from sqlalchemy import String, Column, Boolean
from sqlalchemy.orm import validates

from app import db
from app.exception.validation_error import ValidationError
from app.models.base import BaseModel
from app.utils.mixins import SerializerMixin, TimestampMixin, CRUDMixin
from app.utils.utils import hash_password

username_regex = re.compile(r'^[a-zA-Z0-9_]{3,16}$')


class User(db.Model, TimestampMixin, SerializerMixin, CRUDMixin, BaseModel):
    __tablename__ = 'users'

    email = Column(String(120), unique=False, nullable=False)
    username = Column(String(80), unique=True, nullable=False)
    password = Column(String(128), nullable=False)
    email_confirmed = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def password_matches(self, password):
        return hash_password(password) == self.password

    @validates("email")
    def validate_email(self, key, value):
        if not value:
            raise ValidationError("Email is required.")
        user = User.query.filter_by(email=value).first()
        if user and user.email_confirmed:
            raise ValidationError("Email already in use.")

        email_validator.validate_email(value)

        return value

    @validates("username")
    def validate_username(self, key, value):
        if not value:
            raise ValidationError("Username is required.")
        if not username_regex.match(value):
            raise ValidationError(
                "Invalid username. Must be between 3 and 16 characters, and can only contain letters, numbers, and underscores."
            )
        if User.query.filter_by(username=value).first():
            raise ValidationError("Username already in use.")
        return value

    @validates("password")
    def validate_password(self, key, value):
        if not value:
            raise ValidationError("Password is required.")
        if len(value) < 16 or len(value) > 128:
            raise ValidationError("Invalid password. Must be between 16 and 128 characters.")
        return hash_password(value)

    @validates("is_admin")
    def validate_is_admin(self, key, value):
        if not value or not isinstance(value, bool):
            return False
        return value

    def dump(self):
        return self.to_dict(exclude=["password", "updated_at"])