from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Organization(Base):
    __tablename__ = "organizations"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    borrower = Column(Integer, nullable=False)
    lender = Column(Integer, nullable=False)
    start_date = Column(Integer)
    end_date = Column(Integer)
    state = Column(Integer)

class Log(Base):
    __tablename__ = "logs"
    id = Column(Integer, primary_key=True, index=True)
    action = Column(Integer)
    log_id = Column(Integer, unique=True)
    person = Column(Integer)
    time = Column(Integer)

class Locker(Base):
    __tablename__ = "lockers"
    id = Column(Integer, primary_key=True, index=True)
    state = Column(Integer)
