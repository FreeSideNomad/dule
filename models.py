from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class TrainingSet(Base):
    __tablename__ = 'training_sets'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)

class TrainingMessage(Base):
    __tablename__ = 'training_messages'
    id = Column(Integer, primary_key=True, autoincrement=True)
    training_set_id = Column(Integer, ForeignKey('training_sets.id'), nullable=False)
    role = Column(String(50), nullable=False)
    content = Column(Text, nullable=False)
    training_set = relationship('TrainingSet', back_populates='messages')

TrainingSet.messages = relationship('TrainingMessage', order_by=TrainingMessage.id, back_populates='training_set')

class Session(Base):
    __tablename__ = 'sessions'
    id = Column(Integer, primary_key=True, autoincrement=True)
    training_set_id = Column(Integer, ForeignKey('training_sets.id'), nullable=False)
    start_time = Column(DateTime, server_default=func.current_timestamp())
    training_set = relationship('TrainingSet')

class SessionMessage(Base):
    __tablename__ = 'session_messages'
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey('sessions.id'), nullable=False)
    role = Column(String(50), nullable=False)
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, server_default=func.current_timestamp())
    session = relationship('Session', back_populates='messages')

Session.messages = relationship('SessionMessage', order_by=SessionMessage.id, back_populates='session')