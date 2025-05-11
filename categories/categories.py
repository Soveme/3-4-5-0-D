from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from core.database import get_db
from core.base import CRUDBase
from core.utils import get_current_user
from users.usermodels import User
from .categorymodels import Category, CategoryCreate, CategoryUpdate, CategorySchema

class CategoryDomain(CRUDBase[Category, CategoryCreate, CategoryUpdate]):
    def __init__(self):
        super().__init__(Category)
        self.router = APIRouter(prefix="/categories", tags=["categories"])
        self._register_routes()

    def initialize_default_categories(self, db: Session):
        default_categories = ["Еда", "Транспорт", "Развлечения", "Жилье", "Здоровье"]
        for name in default_categories:
            if not db.query(Category).filter(Category.name == name).first():
                db_category = Category(name=name)
                db.add(db_category)
        db.commit()

    def _register_routes(self):
        @self.router.post("/", response_model=CategorySchema)
        def create_category(
            category_in: CategoryCreate,
            current_user: User = Depends(get_current_user),
            db: Session = Depends(get_db)
        ):
            return self.create(db=db, obj_in=category_in)

        @self.router.get("/", response_model=List[CategorySchema])
        def read_categories(
            current_user: User = Depends(get_current_user),
            db: Session = Depends(get_db)
        ):
            self.initialize_default_categories(db)
            return self.get_multi(db)

        @self.router.put("/{category_id}", response_model=CategorySchema)
        def update_category(
            category_id: int,
            category_in: CategoryUpdate,
            current_user: User = Depends(get_current_user),
            db: Session = Depends(get_db)
        ):
            db_category = self.get(db, id=category_id)
            if not db_category:
                raise HTTPException(status_code=404, detail="Category not found")
            return self.update(db, db_obj=db_category, obj_in=category_in)

        @self.router.delete("/{category_id}", response_model=CategorySchema)
        def delete_category(
            category_id: int,
            current_user: User = Depends(get_current_user),
            db: Session = Depends(get_db)
        ):
            db_category = self.get(db, id=category_id)
            if not db_category:
                raise HTTPException(status_code=404, detail="Category not found")
            return self.delete(db, id=category_id)

    def get_router(self):
        return self.router