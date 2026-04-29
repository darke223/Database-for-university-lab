from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.responses import RedirectResponse
from app.templates import templates
from sqlalchemy.orm import Session
from pydantic import ValidationError

from app.database import SessionLocal
from app.models.result import Result
from app.models.experiment import Experiment
from app.schemas.json_schemas import ResultMeasurements

router = APIRouter(prefix="/results", tags=["results"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/experiment/{experiment_id}")
def result_create_or_update(
    experiment_id: int,
    temperature: float = Form(None),
    strain_rate: float = Form(None),
    max_stress: float = Form(None),
    db: Session = Depends(get_db)
):
    try:
        measurements = ResultMeasurements(
            temperature_c=temperature,
            strain_rate_s1=strain_rate,
            max_stress_mpa=max_stress
        )
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))

    exp = db.query(Experiment).filter(Experiment.id_experiment == experiment_id).first()
    if not exp:
        raise HTTPException(status_code=404, detail="Эксперимент не найден")

    if exp.result:
        exp.result.measurements = measurements.model_dump()
    else:
        new_result = Result(measurements=measurements.model_dump())
        db.add(new_result)
        db.flush()
        exp.id_result = new_result.id_result

    db.commit()
    return RedirectResponse(f"/experiments/{experiment_id}", status_code=303)
