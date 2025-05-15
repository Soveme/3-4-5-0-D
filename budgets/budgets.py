from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import List
from core.database import get_db
from core.base import CRUDBase
from core.utils import get_current_user
from users.usermodels import User
from expenses.expensemodels import Expense
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

    def _register_routes(self):
        @self.router.post("/", response_model=BudgetSchema)
        def create_budget(
                budget_in: BudgetCreate,
                current_user: User = Depends(get_current_user),
                db: Session = Depends(get_db)
        ):
            return self.create(db=db, obj_in=budget_in, user_id=current_user.id)

        @self.router.get("/{id}", response_model=BudgetSchema)
        def read_budget(
                id: int,
                current_user: User = Depends(get_current_user),
                db: Session = Depends(get_db)
        ):
            return self.get(db=db, id=id, user_id=current_user.id)

        @self.router.get("/", response_model=List[BudgetSchema])
        def read_budgets(
                skip: int = 0,
                limit: int = 100,
                current_user: User = Depends(get_current_user),
                db: Session = Depends(get_db)
        ):
            return self.get_multi(db=db, user_id=current_user.id, skip=skip, limit=limit)

        @self.router.put("/{id}", response_model=BudgetSchema)
        def update_budget(
                id: int,
                budget_in: BudgetUpdate,
                current_user: User = Depends(get_current_user),
                db: Session = Depends(get_db)
        ):
            return self.update(db=db, id=id, obj_in=budget_in, user_id=current_user.id)

        @self.router.delete("/{id}", response_model=BudgetSchema)
        def delete_budget(
                id: int,
                current_user: User = Depends(get_current_user),
                db: Session = Depends(get_db)
        ):
            return self.delete(db=db, id=id, user_id=current_user.id)

        @self.router.get("/exceeded", response_model=List[BudgetSchema])
        def get_exceeded_budgets(
                current_user: User = Depends(get_current_user),
                db: Session = Depends(get_db)
        ):
            return self.get_exceeded_budgets(db, user_id=current_user.id)

    def get_router(self):
        return self.router