from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.database import Base, engine, SessionLocal
from auth.auth import AuthDomain
from users.users import UserDomain
from expenses.expenses import ExpenseDomain
from categories.categories import CategoryDomain
from budgets.budgets import BudgetDomain
from groups.groups import GroupDomain
from groups.groupmembers import GroupMemberDomain


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

def include_domains():
    domains = [
        AuthDomain(),
        UserDomain(),
        ExpenseDomain(),
        CategoryDomain(),
        BudgetDomain(),
        GroupDomain(),
        GroupMemberDomain()
    ]
    for domain in domains:
        app.include_router((domain.get_router()))

include_domains()