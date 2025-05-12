from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from core.database import get_db
from core.base import CRUDBase
from core.utils import get_user_by_email, get_current_user
from .usermodels import User, UserCreate, UserUpdate, UserSchema


class UserDomain(CRUDBase[User, UserCreate, UserUpdate]):
    def __init__(self):
        super().__init__(User)
        self.router = APIRouter(prefix="/users", tags=["users"])
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self._register_routes()

    def get_by_email(self, db: Session, email: str) -> User:
        return get_user_by_email(db, email)

    def create(self, db: Session, obj_in: UserCreate) -> User:
        hashed_password = self.pwd_context.hash(obj_in.password)
        db_user = User(email=obj_in.email, hashed_password=hashed_password)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    def update(self, db: Session, id: int, obj_in: UserUpdate) -> User:
        db_obj = self.get(db, id=id)
        update_data = obj_in.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_obj, key, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, id: int) -> User:
        db_obj = self.get(db, id=id)
        db.delete(db_obj)
        db.commit()
        return db_obj

    def _register_routes(self):
        @self.router.post("/", response_model=UserSchema)
        def create_user(user_in: UserCreate, db: Session = Depends(get_db)):
            db_user = self.get_by_email(db, email=user_in.email)
            if db_user:
                raise HTTPException(status_code=400, detail="Email already registered")
            return self.create(db=db, obj_in=user_in)

        @self.router.get("/me", response_model=UserSchema)
        def get_me(user: User = Depends(get_current_user)):
            return user

        @self.router.put("/{id}", response_model=UserSchema)
        def update_user(
                id: int,
                user_in: UserUpdate,
                current_user: User = Depends(get_current_user),
                db: Session = Depends(get_db)
        ):
            if id != current_user.id:
                raise HTTPException(status_code=403, detail="Cannot update another user")
            if user_in.password:
                user_in.password = self.pwd_context.hash(user_in.password)
            return self.update(db=db, id=id, obj_in=user_in)

        @self.router.delete("/{id}", response_model=UserSchema)
        def delete_user(
                id: int,
                current_user: User = Depends(get_current_user),
                db: Session = Depends(get_db)
        ):
            if id != current_user.id:
                raise HTTPException(status_code=403, detail="Cannot delete another user")
            return self.delete(db=db, id=id)

    def get_router(self):
        return self.router