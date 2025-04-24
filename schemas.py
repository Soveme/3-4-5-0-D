from pydantic import BaseModel
from datetime import date
from typing import Optional

class ExpenseBase(BaseModel):
    amount: float
    category_id: int
    date: date
    description: Optional[str] = None

class ExpenseCreate(ExpenseBase):
    pass

class Expense(ExpenseBase):
    id: int
    user_id: int
    class Config:
        orm_mode = True

class CategoryBase(BaseModel):
    name: str

class CategoryCreate(CategoryBase):
    pass

class Category(CategoryBase):
    id: int
    class Config:
        orm_mode = True

class BudgetBase(BaseModel):
    category_id: int
    amount: float
    period: str

class BudgetCreate(BudgetBase):
    pass

class Budget(BudgetBase):
    id: int
    class Config:
        orm_mode = True

class GroupBase(BaseModel):
    name: str

class GroupCreate(GroupBase):
    admin_id: int

class Group(GroupBase):
    id: int
    admin_id: int
    class Config:
        orm_mode = True