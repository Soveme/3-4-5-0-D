from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from pydantic import BaseModel
from typing import Optional
from core.database import Base


class Group(Base):
    __tablename__ = "groups"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    admin_id = Column(Integer, ForeignKey("users.id"))
    admin = relationship("User", back_populates="groups")
    members = relationship("GroupMember", back_populates="group")

class GroupMember(Base):
    __tablename__ = "group_members"
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    group_id = Column(Integer, ForeignKey("groups.id"), primary_key=True)
    user = relationship("User", back_populates="group_memberships")
    group = relationship("Group", back_populates="members")

class GroupBase(BaseModel):
    name: str

class GroupCreate(GroupBase):
    admin_id: Optional[int] = None

class GroupSchema(GroupBase):
    id: int
    admin_id: int
    class Config:
        orm_mode = True

class GroupMemberCreate(BaseModel):
    email: str