from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from pydantic import BaseModel
from typing import Optional
from core.database import Base


class GroupMember(Base):
    __tablename__ = "group_members"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    group_id = Column(Integer, ForeignKey("groups.id"))
    role = Column(String, default="viewer")  # viewer, editor
    user = relationship("User", back_populates="group_memberships")
    group = relationship("Group", back_populates="members")

class GroupMemberBase(BaseModel):
    user_id: int
    group_id: int
    role: str = "viewer"

class GroupMemberCreate(GroupMemberBase):
    pass

class GroupMemberUpdate(GroupMemberBase):
    user_id: Optional[int] = None
    group_id: Optional[int] = None
    role: Optional[str] = None

class GroupMemberSchema(GroupMemberBase):
    id: int
    class Config:
        orm_mode = True