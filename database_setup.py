from sqlalchemy import Column, ForeignKey, Integer, String, Float, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy import create_engine
from sqlalchemy.ext.hybrid import hybrid_property
from flask_login import UserMixin
from datetime import date
import os

Base = declarative_base()

class User(Base, UserMixin):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    firstName = Column(String(80), nullable=False)
    lastName = Column(String(80), nullable=False)
    email = Column(String(80), nullable=False)
    password = Column(String(80), nullable=False)

class Promotional(Base):
    __tablename__ = 'promotional'

    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    type = Column(String(20), nullable=False)
    applications = relationship("Application", back_populates="promotional")

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
    payment = Column(String(80))
    age = Column(Integer, nullable=False)
    rank = Column(Integer, nullable=False)
    number = Column(Integer)
    color = Column(String(20), nullable=False)
    beltSize = Column(String(20), nullable=False)
    promotional_id = Column(Integer, ForeignKey('promotional.id'))
    promotional = relationship("Promotional", back_populates="applications")
    sideA_id = Column(Integer, ForeignKey('application.id'))
    sideB_id = Column(Integer, ForeignKey('application.id'))
    sideA = relationship("Application", foreign_keys=[sideA_id], post_update=True, uselist=False)
    sideB = relationship("Application", foreign_keys=[sideB_id], post_update=True, uselist=False)

    def partner(self):
        if self.sideA:
            return self.sideA
        return self.sideB
    
    def partnerInfo(self):
        if self.sideA:
            return self.sideA.fullName + " - " + self.rankDict[self.sideA.rank]
        elif self.sideB:
            return self.sideB.fullName + " - " + self.rankDict[self.sideB.rank]
        else:
            return "SUB"
    
    # sideB_id = Column(Integer, ForeignKey('application.id'))
    # sideA = relationship('Application', backref=backref('sideB', remote_side=[id]))

    @hybrid_property
    def fullName(self):
        return self.firstName + " " + self.lastName

    rankDict = ["10th kyu","9th kyu","8th kyu","7th kyu","6th kyu","5th kyu","4th kyu","3rd kyu","2nd kyu",
        "1st kyu","1st dan","2nd dan","3rd dan","4th dan","5th dan","6th dan","7th dan","8th dan","9th dan","10th dan"]

    @hybrid_property
    def rankInfo(self):
        return self.rankDict[self.rank]


    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
        }

class Pairing(Base):
    __tablename__ = 'pairing'

    id = Column(Integer, primary_key=True)
    promotional_id = Column(Integer, ForeignKey('promotional.id'))
    color = Column(String(20), nullable=False)
    sideA_id = Column(Integer, ForeignKey('application.id'))
    sideB_id = Column(Integer, ForeignKey('application.id'))
    application_A = relationship("Application", foreign_keys=[sideA_id], backref="pairingA")
    application_B = relationship("Application", foreign_keys=[sideB_id], backref="pairingB")
    promotional = relationship("Promotional")

engine = create_engine(os.environ['DATABASE_URL'])

Base.metadata.create_all(engine)
