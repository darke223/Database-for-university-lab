from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request

from app.database import engine
from app.models.base import Base
from app.routers import experiments, customers, contracts
from app.routers import experiments, customers, contracts, materials

app = FastAPI(title="Lab Database")

templates = Jinja2Templates(directory="app/templates")

def init_db():
    Base.metadata.create_all(bind=engine)

app.include_router(experiments.router)
app.include_router(customers.router)
app.include_router(contracts.router)
app.include_router(materials.router)

@app.on_event("startup")
def on_startup():
    init_db()

# Главная страница
@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})