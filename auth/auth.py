from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel
from sqlalchemy.orm import Session
from core.database import get_db
from core.config import settings
from core.utils import authenticate_user


templates_mobile = Jinja2Templates(directory="templates/mobile")

class Token(BaseModel):
    access_token: str
    token_type: str

class AuthDomain:
    def __init__(self):
        self.router = APIRouter(prefix="/auth", tags=["auth"])
        self.templates_mobile = templates_mobile
        self._register_routes()

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now() + expires_delta
        else:
            expire = datetime.now() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt

    def decode_access_token(self, token: str):
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

    def _register_routes(self):
        @self.router.post("/token", response_model=Token)
        def login_for_access_token(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
            user = authenticate_user(db, email=form_data.username, password=form_data.password)
            if not user:
                return self.templates_mobile.TemplateResponse(name="entry.html", context={'request': request, "alert": "Неверный логин или пароль"})
            access_token = self.create_access_token(data={"sub": user.email})
            response = RedirectResponse('/dashboard', status_code=302)
            response.set_cookie(
                key="auth_token",
                value=f"Bearer {access_token}",
                max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
                expires=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )
            return response

        @self.router.get("/register", response_class=HTMLResponse)
        async def register_page(request: Request):
            return self.templates_mobile.TemplateResponse(name="register.html", context={'request': request})

        @self.router.get("/login", response_class=HTMLResponse)
        async def login_page(request: Request):
            return self.templates_mobile.TemplateResponse(name="entry.html", context={'request': request})

        @self.router.get("/", response_class=HTMLResponse)
        async def welcome_page(request: Request):
            return self.templates_mobile.TemplateResponse(name="welcome.html", context={'request': request})

    def get_router(self):
        return self.router


#
#
# def verify_password(plain_password, hashed_password):
#     return pwd_context.verify(plain_password, hashed_password)
#
# def get_password_hash(password):
#     return pwd_context.hash(password)
