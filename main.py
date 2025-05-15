from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.database import Base, engine, SessionLocal
from core.utils import default_categories
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

with SessionLocal() as db:
    default_categories(db=db, group_id=0, user_id=0)

def include_domains():
    domains = [
        AuthDomain(),
        UserDomain(),
        ExpenseDomain(),
        CategoryDomain(),
        BudgetDomain(),
        GroupDomain()
    ]
    for domain in domains:
        app.include_router((domain.get_router()))

include_domains()