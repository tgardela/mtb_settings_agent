from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Float, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    bikes = relationship("Bike", back_populates="owner")
    conversations = relationship("Conversation", back_populates="user")
    trails = relationship("Trail", back_populates="user")


class Bike(Base):
    __tablename__ = "bikes"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    brand = Column(String)
    model = Column(String)
    year = Column(Integer)
    suspension_settings = Column(JSON)
    geometry = Column(JSON)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    owner = relationship("User", back_populates="bikes")


class Conversation(Base):
    __tablename__ = "conversations"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    messages = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    user = relationship("User", back_populates="conversations")


class Trail(Base):
    __tablename__ = "trails"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    location = Column(String)
    rating = Column(Float)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    user = relationship("User", back_populates="trails")
