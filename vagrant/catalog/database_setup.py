import sys

from sqlalchemy import Column, ForeignKey, Integer, String

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import relationship

from sqlalchemy import create_engine

Base = declarative_base()

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key = True)
    email = Column(String(80), unique = True, nullable = False)

class Category(Base):
    __tablename__ = 'category'
    id = Column(Integer, primary_key = True)
    name = Column(String(80), nullable = False)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name
        }

class CategoryItem(Base):
    __tablename__ = 'category_item'
    id = Column(Integer, primary_key = True)
    title = Column(String(80), nullable = False)
    description = Column(String(250))

    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'category_id': self.category_id
        }

#######insert at end of File ##############

#engine = create_engine('sqlite:///catalog.db')

# NOTE: to create the database:
# sudo -u postgres psql
# postgres=# create database postgres_catalog;
# postgres=# create user udacity with encrypted password 'n0pedy';
# postgres=# grant all privileges on database postgres_catalog to udacity;
engine = create_engine('postgresql://udacity:n0pedy@localhost/postgres_catalog')

Base.metadata.create_all(engine)

