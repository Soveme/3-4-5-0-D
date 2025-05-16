from fastapi import FastAPI, Request, Depends, Cookie
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from starlette.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from core.database import Base, engine, SessionLocal, get_db
from core.utils import default_categories, get_current_user
from auth.auth import AuthDomain
from users.usermodels import User
from users.users import UserDomain
from expenses.expenses import ExpenseDomain
from categories.categories import CategoryDomain
from budgets.budgets import BudgetDomain
from groups.groups import GroupDomain

templates_mobile = Jinja2Templates(directory="templates/mobile")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

Base.metadata.create_all(bind=engine)

@app.get("/", response_class=HTMLResponse)
async def welcome_page(request: Request):
    return templates_mobile.TemplateResponse(name="welcome.html", context={'request': request})

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

client = TestClient(app=app)
@app.get("/dashboard", response_class=HTMLResponse)
async def main_page(request: Request, current_user: User = Depends(get_current_user)):
    cook = request.cookies
    groups = client.get("/groups/", cookies=cook).json()
    expenses = [client.get(f"/expenses/{group['id']}", cookies=cook).json() for group in groups]
    return templates_mobile.TemplateResponse(name="main.html", context={'request': request, 'groups': groups, 'exp': expenses})


# pp.get("/dashboard", response_class=HTMLResponse)
# async def main_page(request: Request, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
#     groups = GroupDomain().get_multi(db=db, user_id=current_user.id)
#     group = groups[0]
#     return