from fastapi import HTTPException
from sqlalchemy.orm import Session
from typing import TypeVar, Generic, Type, List, Optional
from pydantic import BaseModel
from abc import ABC, abstractmethod

Model = TypeVar("ModelType")
CreateSchema = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchema = TypeVar("UpdateSchemaType", bound=BaseModel)

class CRUDBase(Generic[Model, CreateSchema, UpdateSchema], ABC):
    def __init__(self, model: Type[Model]):
        self.model = model

    def create(self, db: Session, obj_in: CreateSchema, user_id: Optional[int] = None) -> Model:
        obj_in_data = obj_in.model_dump(exclude_unset=True)
        if user_id is not None and hasattr(self.model, "user_id") and "user_id" not in obj_in_data:
            obj_in_data["user_id"] = user_id
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_multi(self, db: Session, user_id: Optional[int] = None, skip: int = 0, limit: int = 100) -> List[Model]:
        query = db.query(self.model)
        if user_id is not None and hasattr(self.model, "user_id"):
            query = query.filter(self.model.user_id == user_id)
        return query.offset(skip).limit(limit).all()

    def get(self, db: Session, id: int, user_id: Optional[int] = None) -> Model:
        query = db.query(self.model).filter(self.model.id == id)
        if user_id is not None and hasattr(self.model, "user_id"):
            query = query.filter(self.model.user_id == user_id)
        db_obj = query.first()
        if not db_obj:
            raise HTTPException(status_code=404, detail=f"{self.model.__name__} not found")
        return db_obj

    def update(self, db: Session, id: int, db_obj: Model, obj_in: UpdateSchema, user_id: Optional[int] = None) -> Model:
        db_obj = self.get(db, id=id, user_id=user_id)
        obj_data = obj_in.model_dump(exclude_unset=True)
        for key, value in obj_data.items():
            setattr(db_obj, key, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, id: int, user_id: Optional[int] = None) -> Model:
        db_obj = self.get(db, id=id, user_id=user_id)
        db.delete(db_obj)
        db.commit()
        return db_obj