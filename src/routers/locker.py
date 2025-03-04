from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import models, schemas, crud
from database import SessionLocal

router = APIRouter(prefix="/lockers", tags=["Lockers"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=schemas.LockerCreate)
def create_locker(locker: schemas.LockerCreate, db: Session = Depends(get_db)):
    db_locker = models.Locker(**locker.dict())
    db.add(db_locker)
    db.commit()
    db.refresh(db_locker)
    return db_locker

@router.put("/{locker_id}/change_status")
def change_locker_status(locker_id: int, state: int, db: Session = Depends(get_db)):
    locker = db.query(models.Locker).filter(models.Locker.id == locker_id).first()
    if locker:
        locker.state = state
        db.commit()
        db.refresh(locker)
        return {"message": "Locker status updated"}
    return {"error": "Locker not found"}
