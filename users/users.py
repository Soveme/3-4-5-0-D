from fastapi import APIRouter, Depends, HTTPException, Form, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from starlette.responses import HTMLResponse
from core.database import get_db
from core.base import CRUDBase, UpdateSchema
from core.utils import get_user_by_email, get_current_user
from .usermodels import User, UserCreate, UserUpdate, UserSchema
from groups.groupmodels import Group, GroupCreate
from groups.groupmembermodels import GroupMemberCreate
from groups.groups import GroupDomain


templates_mobile = Jinja2Templates(directory="templates/mobile")

class UserDomain(CRUDBase[User, UserCreate, UserUpdate]):
    def __init__(self):
        super().__init__(User)
        self.router = APIRouter(prefix="/users", tags=["users"])
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.templates_mobile = templates_mobile
        self._register_routes()

    def get_by_email(self, db: Session, email: str) -> User:
        return get_user_by_email(db, email)

    def create(self, db: Session, obj_in: UserCreate) -> User:
        db_obj = User(
            email=obj_in.email,
            hashed_password=self.pwd_context.hash(obj_in.password)
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        group_domain = GroupDomain()
        group = group_domain.create(
            db=db,
            obj_in=GroupCreate(name=f"Personal Group for {db_obj.email}"),
            admin_id=db_obj.id
        )
        group_domain.create_member(
            db=db,
            obj_in=GroupMemberCreate(user_id=db_obj.id, group_id=group.id, role="admin"),
            admin_id=db_obj.id
        )
        return db_obj

    def update(self, db: Session, user: User, obj_in: UserUpdate) -> User:
        update_data = obj_in.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(user, key, value)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def delete(self, db: Session, user = User) -> User:
        db.delete(user)
        db.commit()
        return user

    def _register_routes(self):
        @self.router.post("/", response_model=UserSchema)
        def create_user(request: Request, user_in: UserCreate = Form(), db: Session = Depends(get_db)):
            db_user = self.get_by_email(db, email=user_in.email)
            if db_user:
                return self.templates_mobile.TemplateResponse(name="register.html", context={'request': request, "alert": "Пользователь с таким именем уже есть"})
            self.create(db=db, obj_in=user_in)
            return self.templates_mobile.TemplateResponse(name="entry.html", context={'request': request})

        @self.router.get("/me", response_model=UserSchema)
        def get_me(request: Request, user: User = Depends(get_current_user)):
            return self.templates_mobile.TemplateResponse(name="profile.html", context={'request': request, "user": user})

        @self.router.get("/edit", response_class=HTMLResponse)
        def edit_user(request: Request, user: User = Depends(get_current_user)):
            return self.templates_mobile.TemplateResponse(name="edit-profile.html", context={'request': request, "user": user})

        @self.router.post("/{id}", response_model=UserSchema)
        def update_user(
                id: int,
                email: str = Form(...),
                current_user: User = Depends(get_current_user),
                db: Session = Depends(get_db)
        ):
            if id != current_user.id:
                raise HTTPException(status_code=403, detail="Cannot update another user")
            user_in = UserUpdate(email=email)
            if user_in.password:
                user_in.password = self.pwd_context.hash(user_in.password)
            self.update(db=db, user=current_user, obj_in=user_in)
            return RedirectResponse('/', status_code=302)

        @self.router.get("/{id}", response_model=UserSchema)
        def delete_user(
                id: int,
                current_user: User = Depends(get_current_user),
                db: Session = Depends(get_db)
        ):
            if id != current_user.id:
                raise HTTPException(status_code=403, detail="Cannot delete another user")
            self.delete(db=db, user=current_user)
            return RedirectResponse('/', status_code=302)

    def get_router(self):
        return self.router