from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from core.database import get_db
from core.base import CRUDBase
from core.utils import get_current_user
from users.usermodels import User
from .groupmodels import Group, GroupCreate, GroupUpdate, GroupSchema


class GroupDomain(CRUDBase[Group, GroupCreate, GroupSchema]):
    def __init__(self):
        super().__init__(Group)
        self.router = APIRouter(prefix="/groups", tags=["groups"])
        self._register_routes()

    def create(self, db: Session, obj_in: GroupCreate, admin_id: int) -> Group:
        db_obj = Group(name=obj_in.name, admin_id=admin_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get(self, db: Session, id: int, user_id: int) -> Group:
        group = db.query(Group).filter(Group.id == id).first()
        if not group or (group.admin_id != user_id).first():
            raise HTTPException(status_code=404, detail="Group not found or not authorized")
        return group

    def get_multi(self, db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Group]:
        return db.query(Group).filter(Group.admin_id == user_id).offset(skip).limit(limit).all()

    def update(self, db: Session, id: int, obj_in: GroupUpdate, user_id: int) -> Group:
        db_obj = self.get(db, id=id, user_id=user_id)
        if db_obj.admin_id != user_id:
            raise HTTPException(status_code=403, detail="Only admin can update group")
        update_data = obj_in.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_obj, key, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, id: int, user_id: int) -> Group:
        db_obj = self.get(db, id=id, user_id=user_id)
        if db_obj.admin_id != user_id:
            raise HTTPException(status_code=403, detail="Only admin can delete group")
        db.delete(db_obj)
        db.commit()
        return db_obj

    def _register_routes(self):
        @self.router.post("/", response_model=GroupSchema)
        def create_group(
                group_in: GroupCreate,
                current_user: User = Depends(get_current_user),
                db: Session = Depends(get_db)
        ):
            return self.create(db=db, obj_in=group_in, admin_id=current_user.id)

        @self.router.get("/{id}", response_model=GroupSchema)
        def read_group(
                id: int,
                current_user: User = Depends(get_current_user),
                db: Session = Depends(get_db)
        ):
            return self.get(db=db, id=id, user_id=current_user.id)

        @self.router.get("/", response_model=List[GroupSchema])
        def read_groups(
                skip: int = 0,
                limit: int = 100,
                current_user: User = Depends(get_current_user),
                db: Session = Depends(get_db)
        ):
            return self.get_multi(db=db, user_id=current_user.id, skip=skip, limit=limit)

        @self.router.put("/{id}", response_model=GroupSchema)
        def update_group(
                id: int,
                group_in: GroupUpdate,
                current_user: User = Depends(get_current_user),
                db: Session = Depends(get_db)
        ):
            return self.update(db=db, id=id, obj_in=group_in, user_id=current_user.id)

        @self.router.delete("/{id}", response_model=GroupSchema)
        def delete_group(
                id: int,
                current_user: User = Depends(get_current_user),
                db: Session = Depends(get_db)
        ):
            return self.delete(db=db, id=id, user_id=current_user.id)

    def get_router(self):
        return self.router