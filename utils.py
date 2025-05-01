from sqlalchemy.orm import Session
from models import User, Category, Expense, Budget, Group, GroupMember
from schemas import UserCreate, CategoryCreate, ExpenseCreate, BudgetCreate, GroupCreate
from auth import get_password_hash
from datetime import datetime

def create_user(db: Session, user: UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def create_category(db: Session, category: CategoryCreate, user_id: int = None):
    db_category = Category(**category.model_dump(), user_id=user_id)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

def get_categories(db: Session, user_id: int = None):
    if user_id:
        return db.query(Category).filter((Category.user_id == user_id) | (Category.user_id == None)).all()
    return db.query(Category).filter(Category.user_id == None).all()

def create_expense(db: Session, expense: ExpenseCreate, user_id: int):
    db_expense = Expense(**expense.model_dump(), user_id=user_id, date=expense.date)
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return db_expense

def get_expenses(db: Session, user_id: int, group_id: int = None, category_id: int = None, start_date: datetime = None, end_date: datetime = None):
    query = db.query(Expense).filter(Expense.user_id == user_id)
    if group_id:
        query = query.filter(Expense.group_id == group_id)
    if category_id:
        query = query.filter(Expense.category_id == category_id)
    if start_date:
        query = query.filter(Expense.date >= start_date)
    if end_date:
        query = query.filter(Expense.date <= end_date)
    return query.all()

def create_budget(db: Session, budget: BudgetCreate, user_id: int = None):
    db_budget = Budget(**budget.model_dump(), user_id=user_id)
    db.add(db_budget)
    db.commit()
    db.refresh(db_budget)
    return db_budget

def get_budgets(db: Session, user_id: int = None, group_id: int = None):
    query = db.query(Budget)
    if user_id:
        query = query.filter(Budget.user_id == user_id)
    if group_id:
        query = query.filter(Budget.group_id == group_id)
    return query.all()

def create_group(db: Session, group: GroupCreate, admin_id: int):
    db_group = Group(**group.model_dump(), admin_id=admin_id)
    db.add(db_group)
    db.commit()
    db.refresh(db_group)
    db_member = GroupMember(user_id=admin_id, group_id=db_group.id)
    db.add(db_member)
    db.commit()
    return db_group

def add_group_member(db: Session, group_id: int, user_id: int, admin_id: int):
    group = db.query(Group).filter(Group.id == group_id, Group.admin_id == admin_id).first()
    if not group:
        raise ValueError("Group not found or user is not admin")
    db_member = GroupMember(user_id=user_id, group_id=group_id)
    db.add(db_member)
    db.commit()
    return db_member