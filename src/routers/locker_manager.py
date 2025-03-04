from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import models
from database import SessionLocal

router = APIRouter(prefix="/locker_manager", tags=["Locker Manager"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/assign_item")
def assign_item_to_locker(locker_id: int, db: Session = Depends(get_db)):
    locker = db.query(models.Locker).filter(models.Locker.id == locker_id).first()
    if locker:
        locker.state = 1  # Assume 1 means occupied
        db.commit()
        db.refresh(locker)
        return {"message": "Item assigned to locker"}
    return {"error": "Locker not found"}

@router.post("/open_locker/{locker_id}")
def open_locker(locker_id: int, db: Session = Depends(get_db)):
    locker = db.query(models.Locker).filter(models.Locker.id == locker_id).first()
    if locker:
        return {"message": f"Locker {locker_id} opened"}
    return {"error": "Locker not found"}
