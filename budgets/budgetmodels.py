from sqlalchemy import Column, Integer, Float, String, ForeignKey
from sqlalchemy.orm import relationship
from pydantic import BaseModel
from typing import Optional
from core.database import Base


class Budget(Base):
    __tablename__ = "budgets"
    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"))
    amount = Column(Float)
    period = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=True)
    category = relationship("Category")

class BudgetBase(BaseModel):
    category_id: int
    amount: float
    period: str
    user_id: Optional[int] = None
    group_id: Optional[int] = None

class BudgetCreate(BudgetBase):
    pass

class BudgetSchema(BudgetBase):
    id: int
    class Config:
        orm_mode = True