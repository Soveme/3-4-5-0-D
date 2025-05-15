from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from pydantic import BaseModel
from typing import Optional
from core.database import Base


class Group(Base):
    __tablename__ = "groups"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    admin_id = Column(Integer, ForeignKey("users.id"))
    admin = relationship("User", back_populates="groups")
    members = relationship("GroupMember", back_populates="group", cascade="all, delete-orphan")
    categories = relationship("Category", back_populates="group")
    expenses = relationship("Expense", back_populates="group")
    budgets = relationship("Budget", back_populates="group")

class GroupBase(BaseModel):
    name: str

class GroupCreate(GroupBase):
    pass

class GroupUpdate(GroupBase):
    name: Optional[str] = None

class GroupSchema(GroupBase):
    id: int
    admin_id: int
    class Config:
        orm_mode = True