import shutil
import os
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import SessionLocal
from app.models.experiment import Experiment
from app.models.file import File as FileModel
from app.models.experiment_file import ExperimentFile

router = APIRouter(prefix="/files", tags=["files"])

UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/upload/{experiment_id}")
async def upload_file(
    experiment_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    exp = db.query(Experiment).filter(Experiment.id_experiment == experiment_id).first()
    if not exp:
        raise HTTPException(status_code=404, detail="Эксперимент не найден")

    # Формируем путь: uploads/exp_ID/filename
    exp_dir = os.path.join(UPLOAD_DIR, f"exp_{experiment_id}")
    if not os.path.exists(exp_dir):
        os.makedirs(exp_dir)
    
    file_path = os.path.join(exp_dir, file.filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Сохраняем в БД
    new_file = FileModel(
        file_path=file_path,
        file_type=file.content_type,
        created_at=datetime.utcnow()
    )
    db.add(new_file)
    db.flush()
    
    # Связываем с экспериментом
    assoc = ExperimentFile(id_experiment=experiment_id, id_file=new_file.id_file)
    db.add(assoc)
    db.commit()

    return RedirectResponse(f"/experiments/{experiment_id}", status_code=303)

@router.post("/delete/{file_id}")
async def delete_file(
    file_id: int,
    db: Session = Depends(get_db)
):
    # Находим связь с экспериментом для редиректа
    assoc = db.query(ExperimentFile).filter(ExperimentFile.id_file == file_id).first()
    experiment_id = assoc.id_experiment if assoc else None

    file_record = db.query(FileModel).filter(FileModel.id_file == file_id).first()
    if not file_record:
        raise HTTPException(status_code=404, detail="Файл не найден")

    # Удаляем физически
    if os.path.exists(file_record.file_path):
        os.remove(file_record.file_path)

    # Удаляем из БД (каскадно удалится и из ExperimentFile, если настроено, 
    # но лучше удалить явно если нет каскада)
    if assoc:
        db.delete(assoc)
    db.delete(file_record)
    db.commit()

    if experiment_id:
        return RedirectResponse(f"/experiments/{experiment_id}", status_code=303)
    return RedirectResponse("/experiments/", status_code=303)
