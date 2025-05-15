from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from core.database import get_db
from core.base import CRUDBase
from core.utils import get_current_user, update_increment_budgets, update_increment_expenses
from users.usermodels import User
from .categorymodels import Category, CategoryCreate, CategoryUpdate, CategorySchema

class CategoryDomain(CRUDBase[Category, CategoryCreate, CategoryUpdate]):
    def __init__(self):
        super().__init__(Category)
        self.router = APIRouter(prefix="/categories", tags=["categories"])
        self._register_routes()

    def _register_routes(self):
        @self.router.post("/{group_id}", response_model=CategorySchema)
        def create_category(
                group_id: int,
                category_in: CategoryCreate,
                current_user: User = Depends(get_current_user),
                db: Session = Depends(get_db)
        ):
            return self.create(db=db, obj_in=category_in, group_id=group_id, user_id=current_user.id)

        @self.router.get("/{group_id}/{id}", response_model=CategorySchema)
        def read_category(
                group_id: int,
                id: int,
                current_user: User = Depends(get_current_user),
                db: Session = Depends(get_db)
        ):
            return self.get(db=db, id=id, group_id=group_id, user_id=current_user.id)

        @self.router.get("/{group_id}", response_model=List[CategorySchema])
        def read_categories(
                group_id: int,
                skip: int = 0,
                limit: int = 100,
                current_user: User = Depends(get_current_user),
                db: Session = Depends(get_db)
        ):
            return self.get_multi(db=db, group_id=group_id, user_id=current_user.id, skip=skip, limit=limit)

        @self.router.put("/{group_id}/{id}", response_model=CategorySchema)
        def update_category(
                group_id: int,
                id: int,
                category_in: CategoryUpdate,
                current_user: User = Depends(get_current_user),
                db: Session = Depends(get_db)
        ):
            return self.update(db=db, id=id, obj_in=category_in, group_id=group_id, user_id=current_user.id)

        @self.router.delete("/{group_id}/{id}", response_model=CategorySchema)
        def delete_category(
                group_id: int,
                id: int,
                current_user: User = Depends(get_current_user),
                db: Session = Depends(get_db)
        ):
            update_increment_budgets(db=db, id=id, group_id=group_id)
            update_increment_expenses(db=db, id=id, group_id=group_id)
            return self.delete(db=db, id=id, group_id=group_id, user_id=current_user.id)

    def get_router(self):
        return self.router