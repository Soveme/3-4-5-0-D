from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database import Base, engine, get_db
from schemas import UserCreate, User, CategoryCreate, Category, ExpenseCreate, Expense, BudgetCreate, Budget, GroupCreate, Group, Token
from auth import verify_password, create_access_token, get_current_user
from utils import create_user, get_user_by_email, create_category, get_categories, create_expense, get_expenses, create_budget, get_budgets, create_group, add_group_member
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

@app.post("/users/", response_model=User)
def create_user_endpoint(user: UserCreate, db: Session = Depends(get_db)):
    db_user = get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return create_user(db, user)

@app.post("/token", response_model=Token)
def login_for_access_token(data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = get_user_by_email(db, email=data.username)
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/categories/", response_model=Category)
def create_category_endpoint(category: CategoryCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return create_category(db, category, user_id=current_user.id)

@app.get("/categories/", response_model=list[Category])
def get_categories_endpoint(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return get_categories(db, user_id=current_user.id)

@app.post("/expenses/", response_model=Expense)
def create_expense_endpoint(expense: ExpenseCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return create_expense(db, expense, user_id=current_user.id)

@app.get("/expenses/", response_model=list[Expense])
def get_expenses_endpoint(
    group_id: int = None,
    category_id: int = None,
    start_date: datetime = None,
    end_date: datetime = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return get_expenses(db, user_id=current_user.id, group_id=group_id, category_id=category_id, start_date=start_date, end_date=end_date)

@app.post("/budgets/", response_model=Budget)
def create_budget_endpoint(budget: BudgetCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return create_budget(db, budget, user_id=current_user.id)

@app.get("/budgets/", response_model=list[Budget])
def get_budgets_endpoint(group_id: int = None, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return get_budgets(db, user_id=current_user.id, group_id=group_id)

@app.post("/groups/", response_model=Group)
def create_group_endpoint(group: GroupCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return create_group(db, group, admin_id=current_user.id)

@app.post("/groups/{group_id}/members/")
def add_group_member_endpoint(group_id: int, user_email: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user = get_user_by_email(db, email=user_email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    try:
        return add_group_member(db, group_id=group_id, user_id=user.id, admin_id=current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))
