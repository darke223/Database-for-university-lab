from fastapi import FastAPI

from app.database import engine
from app.models.base import Base

from app.routers import experiments

app = FastAPI(title="Lab Database")

def init_db():
    Base.metadata.create_all(bind=engine)

app.include_router(experiments.router)

@app.on_event("startup")
def on_startup():
    init_db()