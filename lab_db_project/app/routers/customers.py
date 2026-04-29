from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.responses import RedirectResponse
from app.templates import templates
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.customer import Customer

router = APIRouter(prefix="/customers", tags=["customers"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/")
def customers_list(request: Request, db: Session = Depends(get_db)):
    customers = db.query(Customer).all()
    return templates.TemplateResponse(
        "customers_list.html",
        {"request": request, "customers": customers}
    )


@router.get("/new")
def customer_create_form(request: Request):
    return templates.TemplateResponse(
        "customer_form.html",
        {"request": request}
    )


@router.post("/new")
def customer_create(name: str = Form(...), db: Session = Depends(get_db)):
    new_customer = Customer(name=name)
    db.add(new_customer)
    db.commit()
    return RedirectResponse("/customers/", status_code=303)


@router.get("/{customer_id}/edit")
def customer_edit_form(request: Request, customer_id: int, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id_customer == customer_id).first()
    if not customer:
        return templates.TemplateResponse("404.html", {"request": request}, status_code=404)
    return templates.TemplateResponse(
        "customer_form.html",
        {"request": request, "customer": customer, "is_edit": True}
    )


@router.post("/{customer_id}/edit")
def customer_update(customer_id: int, name: str = Form(...), db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id_customer == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Клиент не найден")
    customer.name = name
    db.commit()
    return RedirectResponse("/customers/", status_code=303)


@router.post("/{customer_id}/delete")
def customer_delete(customer_id: int, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id_customer == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Клиент не найден")
    db.delete(customer)
    db.commit()
    return RedirectResponse("/customers/", status_code=303)