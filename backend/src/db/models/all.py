from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Boolean, TIMESTAMP
from sqlalchemy.orm import relationship
from datetime import datetime
from src.db.init_pstgrsql import Base

class File(Base):
    __tablename__ = 'files'

    id = Column(Integer, primary_key=True, autoincrement=True)
    hash = Column(String)
    path = Column(String)
    size = Column(Integer)
    modification_time = Column(Float)
    access_time = Column(Float)
    creation_time = Column(Float)
    date_added = Column(TIMESTAMP, server_default='now()')
    is_deleted = Column(Boolean, default=False)

class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    items = relationship("Item", back_populates="owner")

class Item(Base):
    __tablename__ = 'items'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, index=True)
    owner_id = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="items")