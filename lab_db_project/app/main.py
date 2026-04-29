from fastapi import FastAPI, Request, Depends
from fastapi.responses import RedirectResponse
from app.templates import templates
from sqlalchemy.orm import Session

from fastapi.staticfiles import StaticFiles
from app.database import engine
from app.models.base import Base
from app.routers import experiments, customers, contracts, materials, samples, strikers, results, files

app = FastAPI(title="Lab Database")


app.include_router(experiments.router)
app.include_router(customers.router)
app.include_router(contracts.router)
app.include_router(materials.router)
app.include_router(samples.router)
app.include_router(strikers.router)
app.include_router(results.router)
app.include_router(files.router)

# Разрешаем доступ к файлам из папки uploads
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

@app.on_event("startup")
def on_startup():
    pass

# Главная страница
@app.get("/")
def home(request: Request, db: Session = Depends(experiments.get_db)):
    from app.models.experiment import Experiment
    from app.models.experiment_status import ExperimentStatus
    from sqlalchemy import func

    total_experiments = db.query(Experiment).count()
    status_counts = db.query(
        ExperimentStatus.name, 
        func.count(Experiment.id_experiment)
    ).join(Experiment).group_by(ExperimentStatus.name).all()

    return templates.TemplateResponse(
        "index.html", 
        {
            "request": request, 
            "total": total_experiments,
            "status_counts": dict(status_counts)
        }
    )