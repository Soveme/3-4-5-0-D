from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from budgets.budgetmodels import Budget
from expenses.expensemodels import Expense
from .database import get_db
from .config import settings, pwd_context
from users.usermodels import User
from categories.categorymodels import Category

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

def get_user_by_email(db: Session, email: str) -> User:
    return db.query(User).filter(User.email == email).first()

def authenticate_user(db: Session, email: str, password: str) -> User:
    user = get_user_by_email(db, email)
    if not user or not pwd_context.verify(password, user.hashed_password):
        return None
    return user

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = get_user_by_email(db, email=email)
    if user is None:
        raise credentials_exception
    return user

def default_categories(db: Session, group_id: int, user_id: int):
    categories = [
        "Пополнение",
        "Супермаркеты",
        "Кафе и рестораны",
        "Транспорт",
        "Коммунальные платежи",
        "Связь и интернет",
        "Одежда и обувь",
        "Здоровье и медицина",
        "Развлечения",
        "Путешествия",
        "Дом и ремонт",
        "Переводы",
        "Животные",
        "Прочие расходы"
    ]
    for name in categories:
        if not db.query(Category).filter(Category.name == name).first():
            db_category = Category(name=name, group_id=group_id, created_by=user_id)
            db.add(db_category)
    db.commit()

def update_increment_expenses(db: Session, id: int, group_id: int):
    db_objs = db.query(Expense).filter(Expense.group_id == group_id, Expense.category_id == id).all()
    if db_objs:
        for db_obj in db_objs:
            setattr(db_obj, "category_id", 14)
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)

def update_increment_budgets(db: Session, id: int, group_id: int):
    db_objs = db.query(Budget).filter(Budget.group_id == group_id, Budget.category_id == id).all()
    if db_objs:
        for db_obj in db_objs:
            setattr(db_obj, "category_id", 14)
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)