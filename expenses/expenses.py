from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional, List
from core.database import get_db
from core.base import CRUDBase
from core.utils import get_current_user
from users.usermodels import User
from .expensemodels import Expense, ExpenseCreate, ExpenseUpdate, ExpenseSchema


class ExpenseDomain(CRUDBase[Expense, ExpenseCreate, ExpenseSchema]):
    def __init__(self):
        super().__init__(Expense)
        self.router = APIRouter(prefix="/expenses", tags=["expenses"])
        self._register_routes()

    def create(self, db: Session, obj_in: ExpenseCreate, user_id: int) -> Expense:
        db_expense = Expense(
            amount=obj_in.amount,
            category_id=obj_in.category_id,
            date=obj_in.date,
            description=obj_in.description,
            user_id=user_id
        )
        db.add(db_expense)
        db.commit()
        db.refresh(db_expense)
        return db_expense

    def get(self, db: Session, id: int, user_id: int) -> Expense:
        expense = db.query(Expense).filter(Expense.id == id, Expense.user_id == user_id).first()
        if not expense:
            raise HTTPException(status_code=404, detail="Expense not found or not authorized")
        return expense

    def get_multi(
        self,
        db: Session,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        category_id: Optional[int] = None,
        min_amount: Optional[float] = None,
        max_amount: Optional[float] = None
    ) -> List[Expense]:
        query = db.query(Expense).filter(Expense.user_id == user_id)
        if start_date and end_date:
            query = query.filter(start_date <= Expense.date <= end_date)
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

    def update(self, db: Session, id: int, obj_in: ExpenseUpdate, user_id: int) -> Expense:
        db_obj = self.get(db, id=id, user_id=user_id)
        update_data = obj_in.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_obj, key, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, id: int, user_id: int) -> Expense:
        db_obj = self.get(db, id=id, user_id=user_id)
        db.delete(db_obj)
        db.commit()
        return db_obj

    def _register_routes(self):
        @self.router.post("/", response_model=ExpenseSchema)
        def create_expense(
                expense_in: ExpenseCreate,
                current_user: User = Depends(get_current_user),
                db: Session = Depends(get_db)
        ):
            return self.create(db=db, obj_in=expense_in, user_id=current_user.id)

        @self.router.get("/{id}", response_model=ExpenseSchema)
        def read_expense(
                id: int,
                current_user: User = Depends(get_current_user),
                db: Session = Depends(get_db)
        ):
            return self.get(db=db, id=id, user_id=current_user.id)

        @self.router.get("/", response_model=List[ExpenseSchema])
        def read_expenses(
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
                user_id=current_user.id,
                skip=skip,
                limit=limit,
                start_date=start_date,
                end_date=end_date,
                category_id=category_id,
                min_amount=min_amount,
                max_amount=max_amount
            )

        @self.router.put("/{id}", response_model=ExpenseSchema)
        def update_expense(
                id: int,
                expense_in: ExpenseUpdate,
                current_user: User = Depends(get_current_user),
                db: Session = Depends(get_db)
        ):
            return self.update(db=db, id=id, obj_in=expense_in, user_id=current_user.id)

        @self.router.delete("/{id}", response_model=ExpenseSchema)
        def delete_expense(
                id: int,
                current_user: User = Depends(get_current_user),
                db: Session = Depends(get_db)
        ):
            return self.delete(db=db, id=id, user_id=current_user.id)

    def get_router(self):
        return self.router