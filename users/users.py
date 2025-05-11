from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from core.database import get_db
from core.base import CRUDBase
from core.utils import get_user_by_email, get_current_user
from .usermodels import User, UserCreate, UserSchema



class UserDomain(CRUDBase[User, UserCreate, UserSchema]):
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

    def get_router(self):
        return self.router