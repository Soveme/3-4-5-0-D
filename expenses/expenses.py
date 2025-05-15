from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import or_
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional, List
from core.database import get_db
from core.base import CRUDBase
from core.utils import get_current_user
from users.usermodels import User
from categories.categorymodels import Category
from .expensemodels import Expense, ExpenseCreate, ExpenseUpdate, ExpenseSchema


class ExpenseDomain(CRUDBase[Expense, ExpenseCreate, ExpenseUpdate]):
    def __init__(self):
        super().__init__(Expense)
        self.router = APIRouter(prefix="/expenses", tags=["expenses"])
        self._register_routes()

    def create(self, db: Session, obj_in: ExpenseCreate, group_id: int, user_id: int) -> Expense:
        self._check_group_membership(db, group_id, user_id)
        category = db.query(Category).filter(
            Category.id == obj_in.category_id,
            Category.group_id == group_id
        ).first()
        if not category:
            raise HTTPException(status_code=400, detail="Category not found in this group")
        return super().create(db=db, obj_in=obj_in, group_id=group_id, user_id=user_id)

    def update(self, db: Session, id: int, obj_in: ExpenseUpdate, group_id: int, user_id: int) -> Expense:
        self.get(db, id=id, group_id=group_id, user_id=user_id)
        if obj_in.category_id:
            category = db.query(Category).filter(
                Category.id == obj_in.category_id,
                or_(Category.group_id == group_id, Category.group_id == 0)
            ).first()
            if not category:
                raise HTTPException(status_code=400, detail="Category not found in this group")
        return super().update(db=db, id=id, obj_in=obj_in, group_id=group_id, user_id=user_id)

    def get_multi(
        self,
        db: Session,
        group_id: int,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        category_id: Optional[int] = None,
        min_amount: Optional[float] = None,
        max_amount: Optional[float] = None
    ) -> List[Expense]:
        query = db.query(Expense).filter(Expense.group_id == group_id)
        if start_date:
            query = query.filter(Expense.date >= start_date)
        if end_date:
            query = query.filter(Expense.date <= end_date)
        if category_id:
            query = query.filter(Expense.category_id == category_id)
        if min_amount is not None:
            query = query.filter(Expense.amount >= min_amount)
        if max_amount is not None:
            query = query.filter(Expense.amount <= max_amount)
        return query.offset(skip).limit(limit).all()

    def _register_routes(self):
        @self.router.post("/{group_id}", response_model=ExpenseSchema)
        def create_expense(
                group_id: int,
                expense_in: ExpenseCreate,
                current_user: User = Depends(get_current_user),
                db: Session = Depends(get_db)
        ):
            return self.create(db=db, obj_in=expense_in, group_id=group_id, user_id=current_user.id)

        @self.router.get("/{group_id}/{id}", response_model=ExpenseSchema)
        def read_expense(
                group_id: int,
                id: int,
                current_user: User = Depends(get_current_user),
                db: Session = Depends(get_db)
        ):
            return self.get(db=db, id=id, group_id=group_id, user_id=current_user.id)

        @self.router.get("/{group_id}", response_model=List[ExpenseSchema])
        def read_expenses(
                group_id: int,
                skip: int = 0,
                limit: int = 100,
                start_date: Optional[date] = None,
                end_date: Optional[date] = None,
                category_id: Optional[int] = None,
                min_amount: Optional[float] = None,
                max_amount: Optional[float] = None,
                current_user: User = Depends(get_current_user),
                db: Session = Depends(get_db)
        ):
            return self.get_multi(
                db,
                group_id=group_id,
                user_id=current_user.id,
                skip=skip,
                limit=limit,
                start_date=start_date,
                end_date=end_date,
                category_id=category_id,
                min_amount=min_amount,
                max_amount=max_amount
            )

        @self.router.put("/{group_id}/{id}", response_model=ExpenseSchema)
        def update_expense(
                group_id: int,
                id: int,
                expense_in: ExpenseUpdate,
                current_user: User = Depends(get_current_user),
                db: Session = Depends(get_db)
        ):
            return self.update(db=db, id=id, obj_in=expense_in, group_id=group_id, user_id=current_user.id)

        @self.router.delete("/{group_id}/{id}", response_model=ExpenseSchema)
        def delete_expense(
                group_id: int,
                id: int,
                current_user: User = Depends(get_current_user),
                db: Session = Depends(get_db)
        ):
            return self.delete(db=db, id=id, group_id=group_id, user_id=current_user.id)

    def get_router(self):
        return self.router