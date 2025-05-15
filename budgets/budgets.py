from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, or_
from sqlalchemy.orm import Session
from typing import List
from core.database import get_db
from core.base import CRUDBase
from core.utils import get_current_user
from users.usermodels import User
from expenses.expensemodels import Expense
from categories.categorymodels import Category
from .budgetmodels import Budget, BudgetCreate, BudgetUpdate, BudgetSchema


class BudgetDomain(CRUDBase[Budget, BudgetCreate, BudgetUpdate]):
    def __init__(self):
        super().__init__(Budget)
        self.router = APIRouter(prefix="/budgets", tags=["budgets"])
        self._register_routes()

    def check_budget_exceeded(self, db: Session, budget: Budget) -> bool:
        total_expenses = db.query(func.sum(Expense.amount)).filter(
            Expense.category_id == budget.category_id,
            Expense.user_id == budget.user_id,
            Expense.date >= budget.end_date
        ).scalar() or 0
        return total_expenses > budget.limit

    def get_exceeded_budgets(self, db: Session, user_id: int) -> List[Budget]:
        budgets = db.query(Budget).filter(Budget.user_id == user_id).all()
        return [budget for budget in budgets if self.check_budget_exceeded(db, budget)]

    def create(self, db: Session, obj_in: BudgetCreate, group_id: int, user_id: int) -> Budget:
        self._check_group_membership(db, group_id, user_id)
        category = db.query(Category).filter(
            Category.id == obj_in.category_id,
            or_(Category.group_id == group_id, Category.group_id == 0)
        ).first()
        if not category:
            raise HTTPException(status_code=400, detail="Category not found in this group")
        return super().create(db=db, obj_in=obj_in, group_id=group_id, user_id=user_id)

    def update(self, db: Session, id: int, obj_in: BudgetUpdate, group_id: int, user_id: int) -> Budget:
        self.get(db, id=id, group_id=group_id, user_id=user_id)
        if obj_in.category_id:
            category = db.query(Category).filter(
                Category.id == obj_in.category_id,
                Category.group_id == group_id
            ).first()
            if not category:
                raise HTTPException(status_code=400, detail="Category not found in this group")
        return super().update(db=db, id=id, obj_in=obj_in, group_id=group_id, user_id=user_id)

    def _register_routes(self):
        @self.router.post("/{group_id}", response_model=BudgetSchema)
        def create_budget(
                group_id: int,
                budget_in: BudgetCreate,
                current_user: User = Depends(get_current_user),
                db: Session = Depends(get_db)
        ):
            return self.create(db=db, obj_in=budget_in, group_id=group_id, user_id=current_user.id)

        @self.router.get("/{group_id}/{id}", response_model=BudgetSchema)
        def read_budget(
                group_id: int,
                id: int,
                current_user: User = Depends(get_current_user),
                db: Session = Depends(get_db)
        ):
            return self.get(db=db, id=id, group_id=group_id, user_id=current_user.id)

        @self.router.get("/{group_id}", response_model=List[BudgetSchema])
        def read_budgets(
                group_id: int,
                skip: int = 0,
                limit: int = 100,
                current_user: User = Depends(get_current_user),
                db: Session = Depends(get_db)
        ):
            return self.get_multi(db=db, group_id=group_id, user_id=current_user.id, skip=skip, limit=limit)

        @self.router.put("/{group_id}/{id}", response_model=BudgetSchema)
        def update_budget(
                group_id: int,
                id: int,
                budget_in: BudgetUpdate,
                current_user: User = Depends(get_current_user),
                db: Session = Depends(get_db)
        ):
            return self.update(db=db, id=id, obj_in=budget_in, group_id=group_id, user_id=current_user.id)

        @self.router.delete("/{group_id}/{id}", response_model=BudgetSchema)
        def delete_budget(
                group_id: int,
                id: int,
                current_user: User = Depends(get_current_user),
                db: Session = Depends(get_db)
        ):
            return self.delete(db=db, id=id, group_id=group_id, user_id=current_user.id)

        @self.router.get("/exceeded", response_model=List[BudgetSchema])
        def get_exceeded_budgets(
                current_user: User = Depends(get_current_user),
                db: Session = Depends(get_db)
        ):
            return self.get_exceeded_budgets(db, user_id=current_user.id)

    def get_router(self):
        return self.router