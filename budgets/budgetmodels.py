from sqlalchemy import Column, Integer, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
from pydantic import BaseModel
from typing import Optional
from datetime import date
from core.database import Base


class Budget(Base):
    __tablename__ = "budgets"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    category_id = Column(Integer, ForeignKey("categories.id"))
    limit = Column(Float)
    start_date = Column(Date)
    end_date = Column(Date)
    user = relationship("User")
    category = relationship("Category")

class BudgetBase(BaseModel):
    category_id: int
    limit: float
    start_date: date
    end_date: date
    user_id: Optional[int] = None
    group_id: Optional[int] = None

class BudgetCreate(BudgetBase):
    pass

class BudgetUpdate(BudgetBase):
    category_id: Optional[int] = None
    limit: Optional[float] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None

class BudgetSchema(BudgetBase):
    id: int
    user_id: int
    class Config:
        orm_mode = True