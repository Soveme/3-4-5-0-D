from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import or_
from sqlalchemy.orm import Session
from typing import List
from core.database import get_db
from core.base import CRUDBase
from core.utils import get_current_user
from users.usermodels import User
from .groupmodels import Group, GroupCreate, GroupUpdate, GroupSchema
from .groupmembermodels import GroupMember, GroupMemberCreate, GroupMemberUpdate, GroupMemberSchema


class GroupDomain(CRUDBase[Group, GroupCreate, GroupUpdate]):
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

    def create_member(self, db: Session, obj_in: GroupMemberCreate, admin_id: int) -> GroupMember:
        group = db.query(Group).filter(Group.id == obj_in.group_id, Group.admin_id == admin_id).first()
        if not group:
            raise HTTPException(status_code=403, detail="Only group admin can add members")
        db_obj = GroupMember(
            user_id=obj_in.user_id,
            group_id=obj_in.group_id,
            role=obj_in.role
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get(self, db: Session, id: int, user_id: int) -> Group:
        group = db.query(self.model).filter(self.model.id == id).first()
        if not group or (group.admin_id != user_id and not db.query(GroupMember).filter(GroupMember.group_id == id, GroupMember.user_id == user_id).first()):
            raise HTTPException(status_code=404, detail="Group not found or not authorized")
        return group

    def get_member(self, db: Session, id: int, user_id: int):
        member = db.query(GroupMember).filter(GroupMember.user_id == user_id, GroupMember.group_id == id).first()
        if not member:
            raise HTTPException(status_code=404, detail="Group member not found or not authorized")
        return member

    def get_multi(self, db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Group]:
        return db.query(self.model).filter(or_(self.model.admin_id == user_id, self.model.members.any(GroupMember.user_id == user_id))).offset(skip).limit(limit).all()

    def get_members(self, db: Session, id: int, skip: int = 0, limit: int = 100) -> List[GroupMember]:
        return db.query(GroupMember).filter(GroupMember.group_id == id).offset(skip).limit(limit).all()

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

    def update_member(self, db: Session, id: int, obj_in: GroupMemberUpdate, admin_id: int) -> GroupMember:
        db_obj = self.get_member(db, id=id, user_id=admin_id)
        group = db.query(Group).filter(Group.id == db_obj.group_id, Group.admin_id == admin_id).first()
        if not group:
            raise HTTPException(status_code=403, detail="Only group admin can update members")
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

    def delete_member(self, db: Session, id: int, user_id: int, admin_id: int) -> GroupMember:
        db_obj = self.get_member(db, id=id, user_id=user_id)
        group = db.query(Group).filter(Group.id == db_obj.group_id, Group.admin_id == admin_id).first()
        if not group:
            raise HTTPException(status_code=403, detail="Only group admin can remove members")
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
            group = self.create(db=db, obj_in=group_in, admin_id=current_user.id)
            self.create_member(
                db=db,
                obj_in=GroupMemberCreate(user_id=current_user.id, group_id=group.id, role="admin"),
                admin_id=current_user.id
            )
            return group

        @self.router.post("/{id}/add", response_model=GroupMemberSchema)
        def create_group_member(
                id: int,
                member_in: GroupMemberCreate,
                current_user: User = Depends(get_current_user),
                db: Session = Depends(get_db)
        ):
            member_in.group_id = id
            return self.create_member(db=db, obj_in=member_in, admin_id=current_user.id)

        @self.router.get("/{id}", response_model=GroupSchema)
        def read_group(
                id: int,
                current_user: User = Depends(get_current_user),
                db: Session = Depends(get_db)
        ):
            return self.get(db=db, id=id, user_id=current_user.id)

        @self.router.get("/{id}/{user_id}", response_model=GroupMemberSchema)
        def read_group_member(
                id: int,
                user_id: int,
                current_user: User = Depends(get_current_user),
                db: Session = Depends(get_db)
        ):
            db_obj = self.get_member(db=db, id=id, user_id=user_id)
            return db_obj

        @self.router.get("/", response_model=List[GroupSchema])
        def read_groups(
                skip: int = 0,
                limit: int = 100,
                current_user: User = Depends(get_current_user),
                db: Session = Depends(get_db)
        ):
            return self.get_multi(db=db, user_id=current_user.id, skip=skip, limit=limit)

        @self.router.get("/{id}/", response_model=List[GroupMemberSchema])
        def read_group_members(
                id: int,
                skip: int = 0,
                limit: int = 100,
                current_user: User = Depends(get_current_user),
                db: Session = Depends(get_db)
        ):
            return self.get_members(db=db, id=id, skip=skip, limit=limit)


        @self.router.put("/{id}", response_model=GroupSchema)
        def update_group(
                id: int,
                group_in: GroupUpdate,
                current_user: User = Depends(get_current_user),
                db: Session = Depends(get_db)
        ):
            return self.update(db=db, id=id, obj_in=group_in, user_id=current_user.id)

        @self.router.put("/{id}/edit", response_model=GroupMemberSchema)
        def update_group_member(
                id: int,
                member_in: GroupMemberUpdate,
                current_user: User = Depends(get_current_user),
                db: Session = Depends(get_db)
        ):
            return self.update_member(db=db, id=id, obj_in=member_in, admin_id=current_user.id)

        @self.router.delete("/{id}", response_model=GroupSchema)
        def delete_group(
                id: int,
                current_user: User = Depends(get_current_user),
                db: Session = Depends(get_db)
        ):
            return self.delete(db=db, id=id, user_id=current_user.id)

        @self.router.delete("/{id}/delete", response_model=GroupMemberSchema)
        def delete_group_member(
                id: int,
                user_id: int,
                current_user: User = Depends(get_current_user),
                db: Session = Depends(get_db)
        ):
            return self.delete_member(db=db, id=id, user_id=user_id, admin_id=current_user.id)

    def get_router(self):
        return self.router