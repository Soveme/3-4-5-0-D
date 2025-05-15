from fastapi import HTTPException
from sqlalchemy.orm import Session
from typing import TypeVar, Generic, Type, List
from pydantic import BaseModel
from abc import ABC, abstractmethod
from groups.groupmembermodels import GroupMember

Model = TypeVar("ModelType")
CreateSchema = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchema = TypeVar("UpdateSchemaType", bound=BaseModel)

class CRUDBase(Generic[Model, CreateSchema, UpdateSchema], ABC):
    def __init__(self, model: Type[Model]):
        self.model = model

    def _check_group_membership(self, db: Session, group_id: int, user_id: int) -> None:
        membership = db.query(GroupMember).filter(
            GroupMember.group_id == group_id,
            GroupMember.user_id == user_id
        ).first()
        if not membership:
            raise HTTPException(status_code=403, detail="User is not a member of the group")

    def create(self, db: Session, obj_in: CreateSchema, group_id: int, user_id: int) -> Model:
        self._check_group_membership(db, group_id, user_id)
        obj_in_data = obj_in.model_dump(exclude_unset=True)
        obj_in_data["group_id"] = group_id
        obj_in_data["created_by"] = user_id
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_multi(self, db: Session, group_id: int, user_id: int, skip: int = 0, limit: int = 100) -> List[Model]:
        self._check_group_membership(db, group_id, user_id)
        query = db.query(self.model).filter(self.model.group_id == group_id).offset(skip).limit(limit).all()
        return query

    def get(self, db: Session, id: int, group_id: int, user_id: int) -> Model:
        self._check_group_membership(db, group_id, user_id)
        db_obj = db.query(self.model).filter(self.model.id == id, self.model.group_id == group_id).first()
        if not db_obj:
            raise HTTPException(status_code=404, detail=f"{self.model.__name__} not found")
        return db_obj

    def update(self, db: Session, id: int, obj_in: UpdateSchema, group_id: int, user_id: int) -> Model:
        db_obj = self.get(db, id=id, group_id=group_id, user_id=user_id)
        obj_data = obj_in.model_dump(exclude_unset=True)
        for key, value in obj_data.items():
            setattr(db_obj, key, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, id: int, group_id: int, user_id: int) -> Model:
        db_obj = self.get(db, id=id, group_id=group_id, user_id=user_id)
        db.delete(db_obj)
        db.commit()
        return db_obj