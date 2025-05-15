from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from pydantic import BaseModel
from typing import Optional
from core.database import Base


class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    group_id = Column(Integer, ForeignKey("groups.id"))
    created_by = Column(Integer, ForeignKey("users.id"))
    group = relationship("Group", back_populates="categories")
    creator = relationship("User")

class CategoryBase(BaseModel):
    name: str

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(CategoryBase):
    name: Optional[str] = None

class CategorySchema(CategoryBase):
    id: int
    group_id: int
    created_by: int
    class Config:
        orm_mode = True