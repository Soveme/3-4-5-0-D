from sqlalchemy import Column, Integer, Float, Date, String, ForeignKey
from sqlalchemy.orm import relationship
from core.database import Base
from pydantic import BaseModel
from typing import Optional
from datetime import date


class Expense(Base):
    __tablename__ = "expenses"
    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float)
    category_id = Column(Integer, ForeignKey("categories.id"))
    date = Column(Date)
    description = Column(String, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="expenses")
    category = relationship("Category")

class ExpenseBase(BaseModel):
    amount: float
    category_id: int
    date: date
    description: Optional[str] = None
    user_id: Optional[int] = None

class ExpenseCreate(ExpenseBase):
    pass

class ExpenseUpdate(ExpenseBase):
    amount: Optional[float] = None
    category_id: Optional[int] = None
    date: Optional[date] = None
    description: Optional[str] = None

class ExpenseSchema(ExpenseBase):
    id: int
    user_id: int
    class Config:
        orm_mode = True