from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.responses import RedirectResponse
from app.templates import templates
from sqlalchemy.orm import Session
from pydantic import ValidationError

from app.database import SessionLocal
from app.models.striker import Striker
from app.schemas.json_schemas import StrikerGeometry

router = APIRouter(prefix="/strikers", tags=["strikers"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/")
def strikers_list(request: Request, db: Session = Depends(get_db)):
    strikers = db.query(Striker).all()
    return templates.TemplateResponse("strikers_list.html", {"request": request, "strikers": strikers})

@router.get("/new")
def striker_create_form(request: Request):
    return templates.TemplateResponse("striker_form.html", {"request": request, "is_edit": False})

@router.get("/{striker_id}/edit")
def striker_edit_form(request: Request, striker_id: int, db: Session = Depends(get_db)):
    striker = db.query(Striker).filter(Striker.id_striker == striker_id).first()
    if not striker:
        raise HTTPException(status_code=404, detail="Ударник не найден")
    
    import json
    geom_str = json.dumps(striker.geometric_dimensions, indent=2, ensure_ascii=False)
    
    return templates.TemplateResponse(
        "striker_form.html",
        {
            "request": request,
            "striker": striker,
            "is_edit": True,
            "geom_str": geom_str
        }
    )

@router.post("/{striker_id}/edit")
def striker_update(
    striker_id: int,
    material: str = Form(...),
    geometry_json: str = Form(...),
    db: Session = Depends(get_db)
):
    striker = db.query(Striker).filter(Striker.id_striker == striker_id).first()
    if not striker:
        raise HTTPException(status_code=404, detail="Ударник не найден")
    
    import json
    try:
        striker.material = material
        striker.geometric_dimensions = json.loads(geometry_json)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ошибка JSON: {str(e)}")
        
    db.commit()
    return RedirectResponse("/strikers/", status_code=303)

@router.post("/new")
def striker_create(
    material: str = Form(...),
    geometry_json: str = Form(...),
    db: Session = Depends(get_db)
):
    import json
    try:
        geom_data = json.loads(geometry_json)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ошибка в формате JSON: {str(e)}")

    new_striker = Striker(
        material=material,
        geometric_dimensions=geom_data
    )
    db.add(new_striker)
    db.commit()
    return RedirectResponse("/strikers/", status_code=303)

@router.post("/{striker_id}/delete")
def striker_delete(striker_id: int, db: Session = Depends(get_db)):
    striker = db.query(Striker).filter(Striker.id_striker == striker_id).first()
    if not striker:
        raise HTTPException(status_code=404, detail="Ударник не найден")
    
    # Проверка на использование в экспериментах
    from app.models.experiment import Experiment
    has_exp = db.query(Experiment).filter(Experiment.id_striker == striker_id).first()
    if has_exp:
        raise HTTPException(status_code=400, detail="Нельзя удалить ударник, используемый в экспериментах")

    db.delete(striker)
    db.commit()
    return RedirectResponse("/strikers/", status_code=303)
