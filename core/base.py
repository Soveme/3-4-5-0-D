from sqlalchemy.orm import Session
from typing import TypeVar, Generic, Type, List
from pydantic import BaseModel
from abc import ABC, abstractmethod

Model = TypeVar("ModelType")
CreateSchema = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchema = TypeVar("UpdateSchemaType", bound=BaseModel)

class CRUDBase(Generic[Model, CreateSchema, UpdateSchema], ABC):
    def __init__(self, model: Type[Model]):
        self.model = model

    def create(self, db: Session, obj_in: CreateSchema) -> Model:
        obj_in_data = obj_in.model_dump(exclude_unset=True)
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_multi(self, db: Session, skip: int = 0, limit: int = 100) -> List[Model]:
        return db.query(self.model).offset(skip).limit(limit).all()

    def get(self, db: Session, id: int) -> Model:
        return db.query(self.model).filter(self.model.id == id).first()

    def update(self, db: Session, db_obj: Model, obj_in: UpdateSchema) -> Model:
        obj_data = obj_in.model_dump(exclude_unset=True)
        for key, value in obj_data.items():
            setattr(db_obj, key, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, id: int) -> Model:
        obj = db.query(self.model).filter(self.model.id == id).first()
        if obj:
            db.delete(obj)
            db.commit()
        return obj