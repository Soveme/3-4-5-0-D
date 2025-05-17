from fastapi import FastAPI, Request, Depends, Cookie
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.testclient import TestClient
from starlette.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from core.database import Base, engine, SessionLocal, get_db
from core.utils import default_categories, get_current_user, calculate_expenses, calculate_budget, calculate_balance
from auth.auth import AuthDomain
from users.usermodels import User
from users.users import UserDomain
from expenses.expenses import ExpenseDomain
from categories.categories import CategoryDomain
from budgets.budgets import BudgetDomain
from groups.groups import GroupDomain

templates_mobile = Jinja2Templates(directory="templates/mobile")
templates_pc = Jinja2Templates(directory="templates/pc")

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

@app.get('/check', response_class=HTMLResponse)
async def check(request: Request):
    return templates_mobile.TemplateResponse(name="guide.html", context={'request': request})

client = TestClient(app=app)
@app.get("/dashboard", response_class=HTMLResponse)
async def main_page(request: Request, current_user: User = Depends(get_current_user)):
    cook = request.cookies
    groups = client.get("/groups/", cookies=cook).json()
    expenses = [client.get(f"/expenses/{group['id']}", cookies=cook).json() for group in groups]
    exps = [calculate_expenses(expense) for expense in expenses]
    buds = [calculate_budget(expense) for expense in expenses]
    balances = [calculate_balance(expense) for expense in expenses]
    for group, expense, bud, balance in zip(groups, exps, buds, balances):
        group["expense"] = expense
        group["bud"] = bud
        group["balance"] = balance
    user_agent = request.headers.get("user-agent", "").lower()
    if "iphone" in user_agent or "ipad" in user_agent or "android" in user_agent:
        return templates_mobile.TemplateResponse(name="main.html", context={'request': request, 'groups': groups})

    return templates_pc.TemplateResponse(name="dashboard.html", context={'request': request, 'groups': groups, 'user': current_user})

@app.get("/dashboard/{id}", response_class=HTMLResponse)
async def main_page(request: Request, id: int, current_user: User = Depends(get_current_user)):
    cook = request.cookies
    groups = client.get("/groups/", cookies=cook).json()
    expenses = [client.get(f"/expenses/{group['id']}", cookies=cook).json() for group in groups]
    exps = [calculate_expenses(expense) for expense in expenses]
    buds = [calculate_budget(expense) for expense in expenses]
    balances = [calculate_balance(expense) for expense in expenses]
    for group, expense, bud, balance in zip(groups, exps, buds, balances):
        group["expense"] = expense
        group["bud"] = bud
        group["balance"] = balance
    user_agent = request.headers.get("user-agent", "").lower()
    if "iphone" in user_agent or "ipad" in user_agent or "android" in user_agent:
        return templates_mobile.TemplateResponse(name="main.html", context={'request': request, 'groups': groups})
    current_group = [group for group in groups if group["id"] == id][0]
    current_exp = client.get(f"/expenses/{id}", cookies=cook).json()
    current_cat = client.get(f"/categories/{id}", cookies=cook).json()
    for exp in current_exp:
        for cat in current_cat:
            if exp["category_id"] == cat["id"]:
                exp["category_name"] = cat["name"]
    return templates_pc.TemplateResponse(name="dashboard.html", context={'request': request, 'groups': groups, 'user': current_user, 'cur_group': current_group, 'cur_exp': current_exp, 'cur_cat': current_cat})

# @app.get("/dashboard/{id}/minus", response_class=HTMLResponse)
# async def dep(request: Request, id: int, current_user: User = Depends(get_current_user)):
#     cook = request.cookies
#     current_cat = client.get(f"/categories/{id}", cookies=cook).json()
#     return templates_mobile.TemplateResponse(name="minus.html", context={'request': request, 'group_id': id, 'cur_cat': current_cat})
#
# @app.get("/dashboard/{id}/plus", response_class=HTMLResponse)
# async def dep(request: Request, id: int, current_user: User = Depends(get_current_user)):
#     return templates_mobile.TemplateResponse(name="plus.html", context={'request': request, 'group_id': id})


@app.get('/group/{id}', response_class=HTMLResponse)
async def edit_group(request: Request, id: int, current_user: User = Depends(get_current_user)):
    cook = request.cookies
    group = client.get(f"/groups/{id}", cookies=cook).json()
    return templates_mobile.TemplateResponse(name="edit-group.html", context={'request': request, 'id': id, 'group': group})

@app.get("/history/{id}", response_class=HTMLResponse)
async def operations(request: Request, id: int, current_user: User = Depends(get_current_user)):
    return templates_mobile.TemplateResponse(name="history.html", context={'request': request, 'id': id})

@app.get("/helper/{id}", response_class=HTMLResponse)
async def helper(request: Request, id: int, current_user: User = Depends(get_current_user)):
    user_agent = request.headers.get("user-agent", "").lower()
    if "iphone" in user_agent or "ipad" in user_agent or "android" in user_agent:
        return templates_mobile.TemplateResponse(name="guide.html", context={'request': request, 'id': id})
    # return templates_pc.TemplateResponse(name="dashboard.html", context={'request': request})


@app.get("/c1", response_class=HTMLResponse)
async def check(request: Request):
    return templates_pc.TemplateResponse(name="category.html", context={'request': request})

@app.get("/c2", response_class=HTMLResponse)
async def check(request: Request):
    return templates_pc.TemplateResponse(name="history.html", context={'request': request})

@app.get("/c3", response_class=HTMLResponse)
async def check(request: Request):
    return templates_pc.TemplateResponse(name="helper.html", context={'request': request})

@app.get("/c4", response_class=HTMLResponse)
async def check(request: Request):
    return templates_pc.TemplateResponse(name="create-group.html", context={'request': request})

@app.get("/c5", response_class=HTMLResponse)
async def check(request: Request):
    return templates_pc.TemplateResponse(name="settings.html", context={'request': request})