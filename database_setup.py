from sqlalchemy import Column, ForeignKey, Integer, String, Float, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class Promotional(Base):
    __tablename__ = 'promotional'

    id = Column(Integer, primary_key=True)
    date = Column(String(20), nullable=False)
    type = Column(String(20), nullable=False)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'date': self.date,
            'type': self.type,
            'id': self.id,
        }

class Application(Base):
    __tablename__ = 'application'

    id = Column(Integer, primary_key=True)
    firstName = Column(String(80), nullable=False)
    lastName = Column(String(80), nullable=False)
    birthDate = Column(String(20), nullable=False)
    rank = Column(String(20), nullable=False)
    promotional_id = Column(Integer, ForeignKey('promotional.id'))
    promotional = relationship(Promotional)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
        }

class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))


class Publisher(Base):
    __tablename__ = 'publisher'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'id': self.id,
        }


class Game(Base):
    __tablename__ = 'game'

    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    description = Column(String(250))
    min_players = Column(Integer)
    max_players = Column(Integer)
    price = Column(Float)
    min_length = Column(Integer)
    max_length = Column(Integer)
    publisher_id = Column(Integer, ForeignKey('publisher.id'))
    publisher = relationship(Publisher)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'description': self.description,
            'id': self.id,
            'price': self.price,
            'min_players': self.min_players,
            'max_players': self.max_players,
            'min_length': self.min_length,
            'max_length': self.max_length,
            'publisher': self.publisher.name
        }


engine = create_engine('sqlite:///boardgamecatalog.db')


Base.metadata.create_all(engine)