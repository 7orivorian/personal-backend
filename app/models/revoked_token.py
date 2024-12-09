from datetime import datetime

from marshmallow_sqlalchemy import auto_field, SQLAlchemySchema
from sqlalchemy import Column, String, DateTime

from app import db
from app.models.base import BaseModel
from app.utils.mixins import CRUDMixin, SerializerMixin


class RevokedToken(db.Model, BaseModel, CRUDMixin, SerializerMixin):
    __tablename__ = 'revoked_tokens'

    jti = Column(String(36), unique=True, nullable=False)  # JWT ID
    revoked_at = Column(DateTime, default=datetime.now())

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class RevokedTokenSchema(SQLAlchemySchema):
    class Meta:
        model = RevokedToken
        load_instance = True  # Allows deserialization into model instances
        include_fk = True  # Include foreign keys if applicable
        sqla_session = db.session

    id = auto_field(dump_only=True)
    jti = auto_field()
    revoked_at = auto_field(dump_only=True)
