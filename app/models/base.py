from sqlalchemy.ext.declarative import declarative_base

from app import db

Base = declarative_base()


class BaseModel(Base):
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
