from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.database import Base, engine, SessionLocal
from auth.auth import AuthDomain
from users.users import UserDomain
from expenses.expenses import ExpenseDomain
from categories.categories import CategoryDomain
from budgets.budgets import BudgetDomain
from groups.groups import GroupDomain

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

category_domain = CategoryDomain()
with SessionLocal() as db:
    category_domain.initialize_default_categories(db)

app.include_router(AuthDomain().get_router())
app.include_router(UserDomain().get_router())
app.include_router(ExpenseDomain().get_router())
app.include_router(CategoryDomain().get_router())
app.include_router(BudgetDomain().get_router())
app.include_router(GroupDomain().get_router())