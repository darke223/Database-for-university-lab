from fastapi import APIRouter, Depends, Request, Form, HTTPException, UploadFile, File
from typing import List, Optional
from fastapi.responses import RedirectResponse
from app.templates import templates
from sqlalchemy.orm import Session, selectinload
import sqlalchemy as sa
from datetime import date
import os

from app.database import SessionLocal
from app.models.experiment import Experiment
from app.models.contract import Contract
from app.models.sample import Sample
from app.models.material import Material
from app.models.experiment_type import ExperimentType
from app.models.experiment_status import ExperimentStatus
from app.models.striker import Striker
from app.models.measuring_rod import MeasuringRod

router = APIRouter(prefix="/experiments", tags=["experiments"])


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

@router.get("/search")
def search_experiments(
    request: Request,
    db: Session = Depends(get_db),
    date_from: str = None,
    date_to: str = None,
    material_id: str = None
):
    query = db.query(Experiment).join(Sample).options(
        selectinload(Experiment.sample).selectinload(Sample.material),
        selectinload(Experiment.contract).selectinload(Contract.customer),
        selectinload(Experiment.status)
    )

    if date_from and date_from.strip():
        query = query.filter(Experiment.experiment_date >= date.fromisoformat(date_from))
    if date_to and date_to.strip():
        query = query.filter(Experiment.experiment_date <= date.fromisoformat(date_to))
    
    if material_id and material_id.strip():
        query = query.filter(Sample.id_material == int(material_id))

    results = query.all()
    materials = db.query(Material).all()

    return templates.TemplateResponse(
        "search.html",
        {
            "request": request,
            "experiments": results,
            "materials": materials,
            "filters": {
                "date_from": date_from,
                "date_to": date_to,
                "material_id": material_id
            }
        }
    )

@router.get("/import")
def import_page(request: Request):
    return templates.TemplateResponse("import.html", {"request": request})

@router.post("/import")
async def import_zip(
    zip_file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    import zipfile
    import json
    import io
    import os
    import shutil
    from app.models.material import Material
    from app.models.customer import Customer
    from app.models.contract import Contract
    from app.models.experiment_type import ExperimentType
    from app.models.experiment_status import ExperimentStatus
    from app.models.striker import Striker
    from app.models.result import Result
    from app.models.file import File as FileModel
    from app.models.experiment_file import ExperimentFile

    content = await zip_file.read()
    zip_buffer = io.BytesIO(content)
    
    imported_count = 0
    
    with zipfile.ZipFile(zip_buffer, "r") as z:
        meta_files = [f for f in z.namelist() if f.endswith("meta.json")]
        
        for meta_path in meta_files:
            folder_prefix = meta_path.replace("meta.json", "")
            with z.open(meta_path) as f:
                data = json.loads(f.read().decode("utf-8"))
            
            mat_name = data.get("material")
            material = db.query(Material).filter(Material.name == mat_name).first()
            if not material:
                material = Material(name=mat_name)
                db.add(material)
                db.flush()
            cust_name = data.get("customer")
            customer = db.query(Customer).filter(Customer.name == cust_name).first()
            if not customer:
                customer = Customer(name=cust_name)
                db.add(customer)
                db.flush()
            type_name = data.get("type", "Ударное сжатие")
            exp_type = db.query(ExperimentType).filter(ExperimentType.name == type_name).first()
            if not exp_type:
                exp_type = ExperimentType(name=type_name)
                db.add(exp_type)
                db.flush()
            status_name = data.get("status", "Завершен")
            status = db.query(ExperimentStatus).filter(ExperimentStatus.name == status_name).first()
            if not status:
                status = ExperimentStatus(name=status_name)
                db.add(status)
                db.flush()
            st_data = data.get("striker", {})
            striker = db.query(Striker).filter(Striker.material == st_data.get("material")).first()
            if not striker:
                striker = Striker(material=st_data.get("material"), geometric_dimensions=st_data.get("dimensions"))
                db.add(striker)
                db.flush()
            new_sample = Sample(id_material=material.id_material, geometry=data.get("sample_geometry"), physical_properties=data.get("sample_properties"))
            db.add(new_sample)
            db.flush()
            new_contract = Contract(id_customer=customer.id_customer, date_of_sample_delivery=date.fromisoformat(data.get("date")), delivery_type="Импортировано", technical_specification=f"Импорт эксперимента №{data.get('id_experiment')}")
            db.add(new_contract)
            db.flush()
            from app.models.measuring_rod import MeasuringRod
            rod = db.query(MeasuringRod).first()
            rod_id = rod.id_rod if rod else 1
            new_exp = Experiment(id_sample=new_sample.id_sample, experiment_type_code=exp_type.experiment_type_code, id_status=status.id_status, id_striker=striker.id_striker, loading_rod_id=rod_id, support_rod_id=rod_id, id_contract=new_contract.id_contract, experiment_date=date.fromisoformat(data.get("date")), comments=data.get("comments"))
            db.add(new_exp)
            db.flush()
            if data.get("results"):
                new_res = Result(id_experiment=new_exp.id_experiment, measurements=data.get("results"))
                db.add(new_res)
            upload_dir = "uploads"
            exp_dir = os.path.join(upload_dir, f"exp_{new_exp.id_experiment}")
            if not os.path.exists(exp_dir): os.makedirs(exp_dir)
            files_prefix = f"{folder_prefix}files/"
            experiment_files = [f for f in z.namelist() if f.startswith(files_prefix)]
            for f_path in experiment_files:
                filename = os.path.basename(f_path)
                if not filename: continue
                target_path = os.path.join(exp_dir, filename)
                with z.open(f_path) as src, open(target_path, "wb") as dst: shutil.copyfileobj(src, dst)
                new_file = FileModel(file_path=target_path, file_type="application/octet-stream")
                db.add(new_file)
                db.flush()
                assoc = ExperimentFile(id_experiment=new_exp.id_experiment, id_file=new_file.id_file)
                db.add(assoc)
            imported_count += 1
        db.commit()
    return RedirectResponse(f"/experiments/?imported={imported_count}", status_code=303)

@router.post("/bulk-export")
def bulk_export(
    request: Request,
    experiment_ids: Optional[List[int]] = Form(None),
    db: Session = Depends(get_db)
):
    import json
    import zipfile
    import io
    
    if not experiment_ids:
        # Если ничего не выбрано, просто возвращаемся назад
        return RedirectResponse(url="/experiments/?error=no_selection", status_code=303)
    
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
        for eid in experiment_ids:
            exp = db.query(Experiment).options(
                selectinload(Experiment.sample).selectinload(Sample.material),
                selectinload(Experiment.experiment_type), selectinload(Experiment.status),
                selectinload(Experiment.striker), selectinload(Experiment.loading_rod),
                selectinload(Experiment.support_rod), selectinload(Experiment.contract).selectinload(Contract.customer),
                selectinload(Experiment.result), selectinload(Experiment.files)
            ).filter(Experiment.id_experiment == eid).first()
            if not exp: continue
            meta = {
                "id_experiment": exp.id_experiment, "date": str(exp.experiment_date),
                "type": exp.experiment_type.name, "status": exp.status.name,
                "customer": exp.contract.customer.name, "material": exp.sample.material.name,
                "sample_geometry": exp.sample.geometry, "sample_properties": exp.sample.physical_properties,
                "striker": {"material": exp.striker.material, "dimensions": exp.striker.geometric_dimensions},
                "results": exp.result.measurements if exp.result else None, "comments": exp.comments
            }
            base_path = f"experiment_{eid}/"
            zip_file.writestr(f"{base_path}meta.json", json.dumps(meta, indent=2, ensure_ascii=False))
            for file_record in exp.files:
                if os.path.exists(file_record.file_path):
                    arcname = f"{base_path}files/{os.path.basename(file_record.file_path)}"
                    zip_file.write(file_record.file_path, arcname)
    zip_buffer.seek(0)
    from fastapi.responses import StreamingResponse
    return StreamingResponse(zip_buffer, media_type="application/x-zip-compressed", headers={"Content-Disposition": "attachment; filename=bulk_export.zip"})

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

@router.get("/{experiment_id}/export")
def export_experiment(experiment_id: int, db: Session = Depends(get_db)):
    import json
    import zipfile
    import io
    
    exp = (
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
    
    if not exp:
        raise HTTPException(status_code=404, detail="Эксперимент не найден")

    # Формируем метаданные
    meta = {
        "id_experiment": exp.id_experiment,
        "date": str(exp.experiment_date),
        "type": exp.experiment_type.name,
        "status": exp.status.name,
        "customer": exp.contract.customer.name,
        "material": exp.sample.material.name,
        "sample_geometry": exp.sample.geometry,
        "sample_properties": exp.sample.physical_properties,
        "striker": {
            "material": exp.striker.material,
            "dimensions": exp.striker.geometric_dimensions
        },
        "results": exp.result.measurements if exp.result else None,
        "comments": exp.comments
    }

    # Создаем ZIP в памяти
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
        # Добавляем метаданные
        zip_file.writestr("experiment_meta.json", json.dumps(meta, indent=2, ensure_ascii=False))
        
        # Добавляем прикрепленные файлы
        for file_record in exp.files:
            if os.path.exists(file_record.file_path):
                # Сохраняем во вложенную папку files/ внутри архива
                arcname = f"files/{os.path.basename(file_record.file_path)}"
                zip_file.write(file_record.file_path, arcname)

    zip_buffer.seek(0)
    
    from fastapi.responses import StreamingResponse
    return StreamingResponse(
        zip_buffer,
        media_type="application/x-zip-compressed",
        headers={"Content-Disposition": f"attachment; filename=experiment_{experiment_id}_export.zip"}
    )

@router.post("/bulk-export")
def bulk_export(
    request: Request,
    experiment_ids: List[int] = Form(...),
    db: Session = Depends(get_db)
):
    import json
    import zipfile
    import io
    
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
        for eid in experiment_ids:
            exp = (
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
                .filter(Experiment.id_experiment == eid)
                .first()
            )
            if not exp:
                continue
            
            # Метаданные для одного эксперимента
            meta = {
                "id_experiment": exp.id_experiment,
                "date": str(exp.experiment_date),
                "type": exp.experiment_type.name,
                "status": exp.status.name,
                "customer": exp.contract.customer.name,
                "material": exp.sample.material.name,
                "sample_geometry": exp.sample.geometry,
                "sample_properties": exp.sample.physical_properties,
                "striker": {
                    "material": exp.striker.material,
                    "dimensions": exp.striker.geometric_dimensions
                },
                "results": exp.result.measurements if exp.result else None,
                "comments": exp.comments
            }
            
            # Путь в архиве: exp_ID/
            base_path = f"experiment_{eid}/"
            zip_file.writestr(f"{base_path}meta.json", json.dumps(meta, indent=2, ensure_ascii=False))
            
            for file_record in exp.files:
                if os.path.exists(file_record.file_path):
                    arcname = f"{base_path}files/{os.path.basename(file_record.file_path)}"
                    zip_file.write(file_record.file_path, arcname)

    zip_buffer.seek(0)
    from fastapi.responses import StreamingResponse
    return StreamingResponse(
        zip_buffer,
        media_type="application/x-zip-compressed",
        headers={"Content-Disposition": "attachment; filename=bulk_export.zip"}
    )

