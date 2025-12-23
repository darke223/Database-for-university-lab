from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.experiment import Experiment

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/")
def experiments_list(request: Request, db: Session = Depends(get_db)):
    experiments = db.query(Experiment).all()
    return templates.TemplateResponse(
        "experiments.html",
        {"request": request, "experiments": experiments}
    )