from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import or_
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
                db_category = Category(name=name, user_id=0)
                db.add(db_category)
        db.commit()

    # def create(self, db: Session, obj_in: CategoryCreate) -> Category:
    #     db_obj = Category(name=obj_in.name)
    #     db.add(db_obj)
    #     db.commit()
    #     db.refresh(db_obj)
    #     return db_obj
    #
    def get(self, db: Session, id: int, user_id: int) -> Category:
        query = db.query(self.model).filter(self.model.id == id, or_(self.model.user_id == user_id, self.model.user_id == 0))
        db_obj = query.first()
        if not db_obj:
            raise HTTPException(status_code=404, detail=f"{self.model.__name__} not found")
        return db_obj

    def get_multi(self, db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Category]:
        query = db.query(self.model).filter(or_(self.model.user_id == user_id, self.model.user_id == 0))
        return query.offset(skip).limit(limit).all()
    #
    # def update(self, db: Session, id: int, obj_in: CategoryUpdate) -> Category:
    #     db_obj = self.get(db, id=id)
    #     update_data = obj_in.model_dump(exclude_unset=True)
    #     for key, value in update_data.items():
    #         setattr(db_obj, key, value)
    #     db.add(db_obj)
    #     db.commit()
    #     db.refresh(db_obj)
    #     return db_obj
    #
    # def delete(self, db: Session, id: int) -> Category:
    #     db_obj = self.get(db, id=id)
    #     db.delete(db_obj)
    #     db.commit()
    #     return db_obj

    def _register_routes(self):
        @self.router.post("/", response_model=CategorySchema)
        def create_category(
                category_in: CategoryCreate,
                current_user: User = Depends(get_current_user),
                db: Session = Depends(get_db)
        ):
            return self.create(db=db, obj_in=category_in, user_id=current_user.id)

        @self.router.get("/{id}", response_model=CategorySchema)
        def read_category(
                id: int,
                current_user: User = Depends(get_current_user),
                db: Session = Depends(get_db)
        ):
            return self.get(db=db, id=id, user_id=current_user.id)

        @self.router.get("/", response_model=List[CategorySchema])
        def read_categories(
                skip: int = 0,
                limit: int = 100,
                current_user: User = Depends(get_current_user),
                db: Session = Depends(get_db)
        ):
            return self.get_multi(db=db, user_id=current_user.id, skip=skip, limit=limit)

        @self.router.put("/{id}", response_model=CategorySchema)
        def update_category(
                id: int,
                category_in: CategoryUpdate,
                current_user: User = Depends(get_current_user),
                db: Session = Depends(get_db)
        ):
            return self.update(db=db, id=id, db_obj=Category, obj_in=category_in, user_id=current_user.id)

        @self.router.delete("/{id}", response_model=CategorySchema)
        def delete_category(
                id: int,
                current_user: User = Depends(get_current_user),
                db: Session = Depends(get_db)
        ):
            return self.delete(db=db, id=id, user_id=current_user.id)

    def get_router(self):
        return self.router