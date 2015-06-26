import os
import sys
import datetime
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):
    __tablename__ = 'Users'

    id = Column(Integer, primary_key=True)
    name = Column(String(250))
    email = Column(String(250))
    picture = Column(String(250))

"""Category class"""


class Category(Base):
    __tablename__ = 'Categories'

    name = Column(String(255), nullable=False)
    id = Column(Integer, primary_key=True)

    @property
    def serilaize(self):
        return{
        'name': self.name,
        'id': self.id,
	    }

"""Item Class"""


class Item(Base):
    __tablename__ = 'Items'

    name = Column(String(255), nullable=False)
    id = Column(Integer, primary_key=True)
    category_id = Column(Integer, ForeignKey('Categories.id'))
    category = relationship(Category)
    owner_id = Column(Integer, ForeignKey('Users.id'))
    owner = relationship(User)
    description = Column(String(255))
    created = Column(DateTime, default=datetime.datetime.utcnow)

    @property
    def serilaize(self):
    	return{
	    'name': self.name,
	    'id': self.id,
            'category_id': self.category_id,
	    'owner_id': self.owner_id,
	    'owner': self.owner,
	    'description': self.description,
            'created': self.created,
        }
engine = create_engine('sqlite:///catalog.db')
Base.metadata.create_all(engine)
