from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.responses import RedirectResponse
from app.templates import templates
from sqlalchemy.orm import Session
from pydantic import ValidationError

from app.database import SessionLocal
from app.models.sample import Sample
from app.models.material import Material
from app.schemas.json_schemas import SampleGeometry, PhysicalProperties

router = APIRouter(prefix="/samples", tags=["samples"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/")
def samples_list(request: Request, db: Session = Depends(get_db)):
    samples = db.query(Sample).all()
    return templates.TemplateResponse("samples_list.html", {"request": request, "samples": samples})

@router.get("/new")
def sample_create_form(request: Request, db: Session = Depends(get_db)):
    materials = db.query(Material).all()
    return templates.TemplateResponse("sample_form.html", {"request": request, "materials": materials, "is_edit": False})

@router.get("/{sample_id}/edit")
def sample_edit_form(request: Request, sample_id: int, db: Session = Depends(get_db)):
    sample = db.query(Sample).filter(Sample.id_sample == sample_id).first()
    if not sample:
        raise HTTPException(status_code=404, detail="Образец не найден")
    materials = db.query(Material).all()
    
    import json
    geom_str = json.dumps(sample.geometry, indent=2, ensure_ascii=False)
    phys_str = json.dumps(sample.physical_properties, indent=2, ensure_ascii=False)
    
    return templates.TemplateResponse(
        "sample_form.html", 
        {
            "request": request, 
            "materials": materials, 
            "sample": sample, 
            "is_edit": True,
            "geom_str": geom_str,
            "phys_str": phys_str
        }
    )

@router.post("/{sample_id}/edit")
def sample_update(
    sample_id: int,
    id_material: int = Form(...),
    geometry_json: str = Form(...),
    properties_json: str = Form(...),
    description: str = Form(None),
    db: Session = Depends(get_db)
):
    sample = db.query(Sample).filter(Sample.id_sample == sample_id).first()
    if not sample:
        raise HTTPException(status_code=404, detail="Образец не найден")
    
    import json
    try:
        sample.id_material = id_material
        sample.geometry = json.loads(geometry_json)
        sample.physical_properties = json.loads(properties_json)
        sample.description = description
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ошибка JSON: {str(e)}")
        
    db.commit()
    return RedirectResponse("/samples/", status_code=303)

@router.post("/new")
def sample_create(
    id_material: int = Form(...),
    geometry_json: str = Form(...),
    properties_json: str = Form(...),
    description: str = Form(None),
    db: Session = Depends(get_db)
):
    import json
    try:
        geom_data = json.loads(geometry_json)
        phys_data = json.loads(properties_json)
        
        # Мы убираем жесткую валидацию Pydantic здесь, чтобы дать пользователю "универсальность"
        # Но можно оставить проверку типов, если нужно
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ошибка в формате JSON: {str(e)}")

    new_sample = Sample(
        id_material=id_material,
        geometry=geom_data,
        physical_properties=phys_data,
        description=description
    )
    db.add(new_sample)
    db.commit()
    return RedirectResponse("/samples/", status_code=303)

@router.post("/{sample_id}/delete")
def sample_delete(sample_id: int, db: Session = Depends(get_db)):
    sample = db.query(Sample).filter(Sample.id_sample == sample_id).first()
    if not sample:
        raise HTTPException(status_code=404, detail="Образец не найден")
    
    # Проверка на наличие связей с экспериментами
    from app.models.experiment import Experiment
    has_experiments = db.query(Experiment).filter(Experiment.id_sample == sample_id).first()
    if has_experiments:
        raise HTTPException(status_code=400, detail="Нельзя удалить образец, используемый в экспериментах")

    db.delete(sample)
    db.commit()
    return RedirectResponse("/samples/", status_code=303)
