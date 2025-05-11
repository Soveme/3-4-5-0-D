from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from core.database import get_db
from core.base import CRUDBase
from core.utils import get_current_user, get_user_by_email
from users.usermodels import User, UserSchema
from expenses.expensemodels import Expense, ExpenseSchema
from budgets.budgetmodels import Budget, BudgetCreate, BudgetSchema
from .groupmodels import Group, GroupCreate, GroupSchema, GroupMember, GroupMemberCreate


class GroupDomain(CRUDBase[Group, GroupCreate, GroupSchema]):
    def __init__(self):
        super().__init__(Group)
        self.router = APIRouter(prefix="/groups", tags=["groups"])
        self._register_routes()

    def create(self, db: Session, obj_in: GroupCreate, admin_id: int) -> Group:
        db_group = Group(name=obj_in.name, admin_id=admin_id)
        db.add(db_group)
        db.commit()
        db.refresh(db_group)
        db_member = GroupMember(user_id=admin_id, group_id=db_group.id)
        db.add(db_member)
        db.commit()
        return db_group

    def add_member(self, db: Session, group_id: int, email: str) -> UserSchema:
        user = get_user_by_email(db, email=email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        group = self.get(db, id=group_id)
        if not group:
            raise HTTPException(status_code=404, detail="Group not found")
        if db.query(GroupMember).filter(GroupMember.user_id == user.id, GroupMember.group_id == group_id).first():
            raise HTTPException(status_code=400, detail="User already in group")
        db_member = GroupMember(user_id=user.id, group_id=group_id)
        db.add(db_member)
        db.commit()
        return user

    def get_group_expenses(self, db: Session, group_id: int, skip: int = 0, limit: int = 100) -> List[Expense]:
        return db.query(Expense).join(GroupMember).filter(GroupMember.group_id == group_id).offset(skip).limit(limit).all()

    def get_group_budget(self, db: Session, group_id: int) -> List[Budget]:
        return db.query(Budget).filter(Budget.group_id == group_id).all()

    def _register_routes(self):
        @self.router.post("/", response_model=GroupSchema)
        def create_group(
            group_in: GroupCreate,
            current_user: User = Depends(get_current_user),
            db: Session = Depends(get_db)
        ):
            return self.create(db=db, obj_in=group_in, admin_id=current_user.id)

        @self.router.post("/{group_id}/members/", response_model=UserSchema)
        def add_group_member(
            group_id: int,
            member: GroupMemberCreate,
            current_user: User = Depends(get_current_user),
            db: Session = Depends(get_db)
        ):
            db_group = self.get(db, id=group_id)
            if not db_group:
                raise HTTPException(status_code=404, detail="Group not found")
            if db_group.admin_id != current_user.id:
                raise HTTPException(status_code=403, detail="Only group admin can add members")
            return self.add_member(db=db, group_id=group_id, email=member.email)

        @self.router.get("/{group_id}/expenses/", response_model=List[ExpenseSchema])
        def get_group_expenses(
            group_id: int,
            skip: int = 0,
            limit: int = 100,
            current_user: User = Depends(get_current_user),
            db: Session = Depends(get_db)
        ):
            db_group = self.get(db, id=group_id)
            if not db_group:
                raise HTTPException(status_code=404, detail="Group not found")
            if not db.query(GroupMember).filter(GroupMember.user_id == current_user.id, GroupMember.group_id == group_id).first():
                raise HTTPException(status_code=403, detail="Not a group member")
            return self.get_group_expenses(db, group_id=group_id, skip=skip, limit=limit)

        @self.router.post("/{group_id}/budgets/", response_model=BudgetSchema)
        def create_group_budget(
            group_id: int,
            budget_in: BudgetCreate,
            current_user: User = Depends(get_current_user),
            db: Session = Depends(get_db)
        ):
            from budgets.budgets import BudgetDomain
            db_group = self.get(db, id=group_id)
            if not db_group:
                raise HTTPException(status_code=404, detail="Group not found")
            if db_group.admin_id != current_user.id:
                raise HTTPException(status_code=403, detail="Only group admin can create budgets")
            budget_domain = BudgetDomain()
            budget_in.group_id = group_id
            return budget_domain.create(db=db, obj_in=budget_in)

        @self.router.get("/{group_id}/budgets/", response_model=List[BudgetSchema])
        def get_group_budgets(
            group_id: int,
            current_user: User = Depends(get_current_user),
            db: Session = Depends(get_db)
        ):
            db_group = self.get(db, id=group_id)
            if not db_group:
                raise HTTPException(status_code=404, detail="Group not found")
            if not db.query(GroupMember).filter(GroupMember.user_id == current_user.id, GroupMember.group_id == group_id).first():
                raise HTTPException(status_code=403, detail="Not a group member")
            return self.get_group_budget(db, group_id=group_id)

    def get_router(self):
        return self.router