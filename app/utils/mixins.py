from datetime import datetime

from app import db


class TimestampMixin:
    """Adds created_at and updated_at columns to models."""
    now = datetime.now()
    created_at = db.Column(db.DateTime, default=now, nullable=False)
    updated_at = db.Column(db.DateTime, default=now, onupdate=datetime.now(), nullable=False)


class SerializerMixin:
    """Adds a `to_dict` method for serializing models."""

    def to_dict(self, exclude=None):
        exclude = exclude or []
        if hasattr(self, '__table__'):
            return {
                column.name: getattr(self, column.name)
                for column in self.__table__.columns
                if column.name not in exclude
            }
        raise AttributeError(f"{self.__class__.__name__} does not have a __table__ attribute.")


class CRUDMixin(object):
    """
    A Mixin to offer CRUD(Create, read, update, delete) operations for SQLAlchemy ORM models.
    """
    __table_args__ = {'extend_existing': True}

    @classmethod
    def create(cls, **kwargs):
        """
        Class Method to create an instance of the model.
        """
        instance = cls(**kwargs)
        return instance.save()

    def update(self, commit=True, **kwargs):
        """
        Instance method to update the fields of a model instance.
        """
        for attr, value in kwargs.items():
            if hasattr(self, attr):
                setattr(self, attr, value)
        return commit and self.save() or self

    def save(self, commit=True):
        """
        Instance method to save the model instance to the database.
        """
        try:
            db.session.add(self)
            if commit:
                db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e
        return self

    def delete(self, commit=True):
        """
        Instance method to delete the model instance from the database.
        """
        try:
            db.session.delete(self)
            if commit:
                db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e
        return self
