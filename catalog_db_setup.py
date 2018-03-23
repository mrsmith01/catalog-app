from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
import datetime

Base = declarative_base()

class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    email = Column(String(75), nullable=False)
    name = Column(String(75), nullable=False)
    picture = Column(String(250))
    timestamp = datetime

    @property
    def serialize(self):
        return {
            'id' : self.id,
            'email' : self.email,
            'name' : self.name,
            'picture' : self.picture,
        }


class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    timestamp = datetime
    users_id = Column(Integer,ForeignKey('users.id'))
    users = relationship(Users)

    @property
    def serialize(self):
        return {
        'id' : self.id,
        'name' : self.name,
        }



class Items(Base):
    __tablename__ = 'items'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(String(250))
    timestamp = datetime
    category_id = Column(Integer,ForeignKey('category.id'))
    category = relationship(Category)
    users_id = Column(Integer, ForeignKey('users.id'))
    users = relationship(Users)

    @property
    def serialize(self):
        return {
        'id' : self.id,
        'name' : self.name,
        'description' : self.description,

    }


engine = create_engine('sqlite:///catalogappusers.db')

Base.metadata.create_all(engine)
