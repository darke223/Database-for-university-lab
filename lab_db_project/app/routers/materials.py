from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.material import Material

router = APIRouter(prefix="/materials", tags=["materials"])
templates = Jinja2Templates(directory="app/templates")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/")
def materials_list(request: Request, db: Session = Depends(get_db)):
    materials = db.query(Material).all()
    return templates.TemplateResponse(
        "materials_list.html",
        {"request": request, "materials": materials}
    )


@router.get("/new")
def material_create_form(request: Request):
    return templates.TemplateResponse(
        "material_form.html",
        {"request": request}
    )


@router.post("/new")
def material_create(name: str = Form(...), db: Session = Depends(get_db)):
    new_material = Material(name=name.strip())
    db.add(new_material)
    db.commit()
    return RedirectResponse("/materials/", status_code=303)


@router.get("/{material_id}/edit")
def material_edit_form(request: Request, material_id: int, db: Session = Depends(get_db)):
    material = db.query(Material).filter(Material.id_material == material_id).first()
    if not material:
        return templates.TemplateResponse("404.html", {"request": request}, status_code=404)
    return templates.TemplateResponse(
        "material_form.html",
        {"request": request, "material": material, "is_edit": True}
    )


@router.post("/{material_id}/edit")
def material_update(material_id: int, name: str = Form(...), db: Session = Depends(get_db)):
    material = db.query(Material).filter(Material.id_material == material_id).first()
    if not material:
        raise HTTPException(status_code=404, detail="Материал не найден")
    material.name = name.strip()
    db.commit()
    return RedirectResponse("/materials/", status_code=303)


@router.post("/{material_id}/delete")
def material_delete(material_id: int, db: Session = Depends(get_db)):
    material = db.query(Material).filter(Material.id_material == material_id).first()
    if not material:
        raise HTTPException(status_code=404, detail="Материал не найден")
    db.delete(material)
    db.commit()
    return RedirectResponse("/materials/", status_code=303)