from sqlalchemy import Column, ForeignKey, Integer, String, Float, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.ext.hybrid import hybrid_property

Base = declarative_base()

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
    birthDate = Column(String(20), nullable=False)
    rank = Column(String(20), nullable=False)
    color = Column(String(20), nullable=False)
    promotional_id = Column(Integer, ForeignKey('promotional.id'))
    promotional = relationship("Promotional", back_populates="applications")

    @hybrid_property
    def fullName(self):
        return self.firstName + " " + self.lastName

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
