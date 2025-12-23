# app/routers/experiments.py
from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session, selectinload
from datetime import date

from app.database import SessionLocal
from app.models.experiment import Experiment
from app.models.contract import Contract
from app.models.sample import Sample
from app.models.experiment_type import ExperimentType
from app.models.experiment_status import ExperimentStatus
from app.models.striker import Striker
from app.models.measuring_rod import MeasuringRod

router = APIRouter(prefix="/experiments", tags=["experiments"])
templates = Jinja2Templates(directory="app/templates")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/")
def experiments_list(request: Request, db: Session = Depends(get_db)):
    experiments = db.query(Experiment).options(
        selectinload(Experiment.contract).selectinload(Contract.customer),
        selectinload(Experiment.sample).selectinload(Sample.material)
    ).all()
    return templates.TemplateResponse(
        "experiments_list.html",
        {"request": request, "experiments": experiments}
    )


@router.get("/new")
def experiment_create_form(request: Request, db: Session = Depends(get_db)):
    contracts = db.query(Contract).all()
    samples = db.query(Sample).all()
    types = db.query(ExperimentType).all()
    statuses = db.query(ExperimentStatus).all()
    strikers = db.query(Striker).all()
    rods = db.query(MeasuringRod).all()

    return templates.TemplateResponse(
        "experiment_form.html",
        {
            "request": request,
            "contracts": contracts,
            "samples": samples,
            "types": types,
            "statuses": statuses,
            "strikers": strikers,
            "rods": rods,
        }
    )


@router.post("/new")
def experiment_create(
    db: Session = Depends(get_db),
    id_sample: int = Form(...),
    experiment_type_code: int = Form(...),
    id_status: int = Form(...),
    id_striker: int = Form(...),
    loading_rod_id: int = Form(...),
    support_rod_id: int = Form(...),
    id_contract: int = Form(...),
    experiment_date: str = Form(...),
    comments: str = Form(None),
):
    new_experiment = Experiment(
        id_sample=id_sample,
        experiment_type_code=experiment_type_code,
        id_status=id_status,
        id_striker=id_striker,
        loading_rod_id=loading_rod_id,
        support_rod_id=support_rod_id,
        id_contract=id_contract,
        experiment_date=date.fromisoformat(experiment_date),
        comments=comments or None,
    )
    db.add(new_experiment)
    db.commit()
    db.refresh(new_experiment)

    return RedirectResponse(url="/experiments/", status_code=303)

@router.get("/{experiment_id}")
def experiment_detail(request: Request, experiment_id: int, db: Session = Depends(get_db)):
    experiment = (
        db.query(Experiment)
        .options(
            selectinload(Experiment.sample).selectinload(Sample.material),
            selectinload(Experiment.experiment_type),
            selectinload(Experiment.status),
            selectinload(Experiment.striker),
            selectinload(Experiment.loading_rod),
            selectinload(Experiment.support_rod),
            selectinload(Experiment.contract).selectinload(Contract.customer),
            selectinload(Experiment.result),
            selectinload(Experiment.files)
        )
        .filter(Experiment.id_experiment == experiment_id)
        .first()
    )

    if not experiment:
        return templates.TemplateResponse(
            "404.html",
            {"request": request},
            status_code=404
        )

    return templates.TemplateResponse(
        "experiment_detail.html",
        {"request": request, "exp": experiment}
    )

@router.get("/{experiment_id}/edit")
def experiment_edit_form(request: Request, experiment_id: int, db: Session = Depends(get_db)):
    exp = db.query(Experiment).filter(Experiment.id_experiment == experiment_id).first()
    if not exp:
        return templates.TemplateResponse("404.html", {"request": request}, status_code=404)

    contracts = db.query(Contract).all()
    samples = db.query(Sample).all()
    types = db.query(ExperimentType).all()
    statuses = db.query(ExperimentStatus).all()
    strikers = db.query(Striker).all()
    rods = db.query(MeasuringRod).all()

    return templates.TemplateResponse(
        "experiment_form.html",
        {
            "request": request,
            "exp": exp,
            "contracts": contracts,
            "samples": samples,
            "types": types,
            "statuses": statuses,
            "strikers": strikers,
            "rods": rods,
            "is_edit": True
        }
    )


@router.post("/{experiment_id}/edit")
def experiment_update(
    experiment_id: int,
    db: Session = Depends(get_db),
    id_sample: int = Form(...),
    experiment_type_code: int = Form(...),
    id_status: int = Form(...),
    id_striker: int = Form(...),
    loading_rod_id: int = Form(...),
    support_rod_id: int = Form(...),
    id_contract: int = Form(...),
    experiment_date: str = Form(...),
    comments: str = Form(None),
):
    exp = db.query(Experiment).filter(Experiment.id_experiment == experiment_id).first()
    if not exp:
        raise HTTPException(status_code=404, detail="Эксперимент не найден")

    exp.id_sample = id_sample
    exp.experiment_type_code = experiment_type_code
    exp.id_status = id_status
    exp.id_striker = id_striker
    exp.loading_rod_id = loading_rod_id
    exp.support_rod_id = support_rod_id
    exp.id_contract = id_contract
    exp.experiment_date = date.fromisoformat(experiment_date)
    exp.comments = comments or None

    db.commit()
    return RedirectResponse(url="/experiments/", status_code=303)

@router.post("/{experiment_id}/delete")
def experiment_delete(experiment_id: int, db: Session = Depends(get_db)):
    exp = db.query(Experiment).filter(Experiment.id_experiment == experiment_id).first()
    if not exp:
        raise HTTPException(status_code=404, detail="Эксперимент не найден")

    db.delete(exp)
    db.commit()
    return RedirectResponse(url="/experiments/", status_code=303)