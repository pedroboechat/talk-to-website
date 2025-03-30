""" This file contains the declarative base class """

# Standard libraries
from datetime import date, datetime

# External libraries
from sqlalchemy.orm import declarative_base


# Definition of the declarative base
Base = declarative_base()


# Custom JSON encoder for model serialization
class SerializerMixin:
    def __init__(self, data):
        for field in self.__table__.columns:
            if getattr(field, "name"):
                setattr(self, field.name, data[field.name])

    def convert_dtypes(self, value):
        if isinstance(value, (date, datetime)):
            value = value.isoformat()
        return value

    def to_dict(self):
        return {
            column.name: self.convert_dtypes(getattr(self, column.name))
            for column in self.__table__.columns
        }
