'''
This class is the base for the ORM model.
Notice that this file does not create any table.
It only defines the base class from which SQLAlchemy models inherit.
'''

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass

'''
DeclarativeBase is provided by SQLAlchemy 2.x. It is used to define a base class for ORM models.
class Base(DeclarativeBase):

This creates our application's base class named Base.

Our employee model inherits from this class:

Because Employee inherits from Base, SQLAlchemy recognizes it as an ORM model and registers its table definition in Base.metadata.
'''