from sqlalchemy import Column, ForeignKey, Integer, String, Float, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy import create_engine
from sqlalchemy.ext.hybrid import hybrid_property
from flask_login import UserMixin
from datetime import date

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
    birthDate = Column(Date, nullable=True)
    rank = Column(String(20), nullable=False)
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
            return self.sideA.fullName + " - " + self.sideA.rank
        elif self.sideB:
            return self.sideB.fullName + " - " + self.sideB.rank
        else:
            return "SUB"
    
    # sideB_id = Column(Integer, ForeignKey('application.id'))
    # sideA = relationship('Application', backref=backref('sideB', remote_side=[id]))

    @hybrid_property
    def fullName(self):
        return self.firstName + " " + self.lastName

    @hybrid_property
    def age(self):
        today = date.today()
        return today.year - self.birthDate.year - ((today.month, today.day) < (self.birthDate.month, self.birthDate.day))

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

engine = create_engine('sqlite:///promotional.db')

Base.metadata.create_all(engine)
