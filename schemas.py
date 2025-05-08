from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool
    class Config:
        orm_mode = True

class CategoryBase(BaseModel):
    name: str

class CategoryCreate(CategoryBase):
    pass

class Category(CategoryBase):
    id: int
    user_id: Optional[int]
    class Config:
        orm_mode = True

class ExpenseBase(BaseModel):
    amount: float
    category_id: int
    description: Optional[str] = None

class ExpenseCreate(ExpenseBase):
    date: Optional[datetime] = None
    group_id: Optional[int] = None

class Expense(ExpenseBase):
    id: int
    date: datetime
    user_id: int
    group_id: Optional[int]
    class Config:
        orm_mode = True

class BudgetBase(BaseModel):
    category_id: int
    amount: float
    period: str

class BudgetCreate(BudgetBase):
    group_id: Optional[int] = None

class Budget(BudgetBase):
    id: int
    user_id: Optional[int]
    group_id: Optional[int]
    class Config:
        orm_mode = True

class GroupBase(BaseModel):
    name: str

class GroupCreate(GroupBase):
    admin_id: Optional[int] = None

class Group(GroupBase):
    id: int
    admin_id: int
    class Config:
        orm_mode = True

class GroupMemberCreate(BaseModel):
    email: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None