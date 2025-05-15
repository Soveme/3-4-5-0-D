from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from pydantic import BaseModel
from typing import Optional
from core.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    groups = relationship("Group", back_populates="admin")
    group_memberships = relationship("GroupMember", back_populates="user")

class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    password: str

class UserUpdate(UserBase):
    email: Optional[str] = None
    password: Optional[str] = None

class UserSchema(UserBase):
    id: int
    class Config:
        orm_mode = True