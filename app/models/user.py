from marshmallow import fields, validate, ValidationError, validates
from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field
from sqlalchemy import String, Column, Boolean

from app import db
from app.models.base import BaseModel
from app.utils.mixins import SerializerMixin, TimestampMixin, CRUDMixin
from app.utils.utils import hash_password


class User(db.Model, TimestampMixin, SerializerMixin, CRUDMixin, BaseModel):
    __tablename__ = 'users'

    email = Column(String(120), unique=True, nullable=False)
    username = Column(String(80), unique=True, nullable=False)
    password = Column(String(128), nullable=False)
    email_confirmed = Column(Boolean, default=False)

    def __init__(self, email, username, password):
        super().__init__(email=email, username=username, password=hash_password(password))

    def check_password(self, password):
        return hash_password(password) == self.password


class UserSchema(SQLAlchemySchema):
    id = fields.Int(dump_only=True)
    username = fields.String(
        required=False,
        validate=validate.Length(min=3, max=16)
    )
    password = fields.String(
        required=True,
        load_only=True,  # Prevent password from appearing in serialized output
        validate=validate.Length(min=16, max=128)
    )


class UserCreateSchema(SQLAlchemySchema):
    class Meta:
        model = User
        load_instance = True  # Allows deserialization into model instances
        include_fk = True  # Include foreign keys if applicable
        sqla_session = db.session

    id = auto_field(dump_only=True)
    email = fields.Email(required=True, load_only=True)  # Email validation
    username = fields.String(
        required=True,
        validate=validate.Length(min=3, max=16, error="Username must be between 3 and 16 characters.")
    )
    password = fields.String(
        required=True,
        load_only=True,  # Prevent password from appearing in serialized output
        validate=validate.Length(min=16, max=128, error="Password must be between 16 and 128 characters.")
    )
    email_confirmed = auto_field(load_only=True)
    created_at = auto_field(dump_only=True)
    updated_at = auto_field(dump_only=True, load_only=True)

    @validates("email")
    def validate_email_unique(self, value):
        user = User.query.filter_by(email=value).first()
        if user and user.email_confirmed:
            raise ValidationError("Email already in use.")

    @validates("username")
    def validate_username_unique(self, value):
        if User.query.filter_by(username=value).first():
            raise ValidationError("Username already in use.")
