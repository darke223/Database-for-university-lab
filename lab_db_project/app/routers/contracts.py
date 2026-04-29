from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.responses import RedirectResponse
from app.templates import templates
from sqlalchemy.orm import Session
from datetime import date

from app.database import SessionLocal
from app.models.contract import Contract
from app.models.customer import Customer

router = APIRouter(prefix="/contracts", tags=["contracts"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/")
def contracts_list(request: Request, db: Session = Depends(get_db)):
    contracts = db.query(Contract).all()
    return templates.TemplateResponse(
        "contracts_list.html",
        {"request": request, "contracts": contracts}
    )


@router.get("/new")
def contract_create_form(request: Request, db: Session = Depends(get_db)):
    customers = db.query(Customer).all()
    return templates.TemplateResponse(
        "contract_form.html",
        {"request": request, "customers": customers}
    )


@router.post("/new")
def contract_create(
    id_customer: int = Form(...),
    date_of_sample_delivery: str = Form(...),
    delivery_type: str = Form(...),
    technical_specification: str = Form(None),
    materials_to_study: str = Form(None),
    report: str = Form(None),
    contract_document: str = Form(None),
    db: Session = Depends(get_db)
):
    new_contract = Contract(
        id_customer=id_customer,
        date_of_sample_delivery=date.fromisoformat(date_of_sample_delivery),
        delivery_type=delivery_type,
        technical_specification=technical_specification or None,
        materials_to_study=materials_to_study or None,
        report=report or None,
        contract_document=contract_document or None
    )
    db.add(new_contract)
    db.commit()
    return RedirectResponse("/contracts/", status_code=303)


@router.get("/{contract_id}/edit")
def contract_edit_form(request: Request, contract_id: int, db: Session = Depends(get_db)):
    contract = db.query(Contract).filter(Contract.id_contract == contract_id).first()
    if not contract:
        return templates.TemplateResponse("404.html", {"request": request}, status_code=404)
    customers = db.query(Customer).all()
    return templates.TemplateResponse(
        "contract_form.html",
        {"request": request, "contract": contract, "customers": customers, "is_edit": True}
    )


@router.post("/{contract_id}/edit")
def contract_update(
    contract_id: int,
    id_customer: int = Form(...),
    date_of_sample_delivery: str = Form(...),
    delivery_type: str = Form(...),
    technical_specification: str = Form(None),
    materials_to_study: str = Form(None),
    report: str = Form(None),
    contract_document: str = Form(None),
    db: Session = Depends(get_db)
):
    contract = db.query(Contract).filter(Contract.id_contract == contract_id).first()
    if not contract:
        raise HTTPException(status_code=404, detail="Контракт не найден")
    contract.id_customer = id_customer
    contract.date_of_sample_delivery = date.fromisoformat(date_of_sample_delivery)
    contract.delivery_type = delivery_type
    contract.technical_specification = technical_specification or None
    contract.materials_to_study = materials_to_study or None
    contract.report = report or None
    contract.contract_document = contract_document or None
    db.commit()
    return RedirectResponse("/contracts/", status_code=303)


@router.post("/{contract_id}/delete")
def contract_delete(contract_id: int, db: Session = Depends(get_db)):
    contract = db.query(Contract).filter(Contract.id_contract == contract_id).first()
    if not contract:
        raise HTTPException(status_code=404, detail="Контракт не найден")
    db.delete(contract)
    db.commit()
    return RedirectResponse("/contracts/", status_code=303)