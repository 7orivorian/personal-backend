from datetime import datetime

from sqlalchemy import Column, String, DateTime, Integer, ForeignKey
from sqlalchemy.orm import relationship, validates

from app import db
from app.models.base import BaseModel
from app.utils.mixins import CRUDMixin, SerializerMixin


class RevokedToken(db.Model, BaseModel, CRUDMixin, SerializerMixin):
    __tablename__ = 'revoked_tokens'

    jti = Column(String(36), unique=True, nullable=False)  # JWT ID
    revoked_at = Column(DateTime, default=datetime.now())

    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    user = relationship('User', backref='revoked_tokens')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @validates("jti")
    def validate_jti(self, key, value):
        if not value:
            raise ValueError("JTI is required.")
        if RevokedToken.query.filter_by(jti=value).first():
            raise ValueError("Token already revoked.")
        return value

    @validates("revoked_at")
    def validate_revoked_at(self, key, value):
        if not value:
            raise ValueError("Revoked at is required.")
        return datetime.strptime(value, "%Y-%m-%d").date()

    @validates("user_id")
    def validate_user_id(self, key, value):
        if not value:
            raise ValueError("User ID is required.")
        return value
