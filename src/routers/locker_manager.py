from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import crud
from database import SessionLocal
from services.locker_service import assign_item_to_locker, open_locker

router = APIRouter(prefix="/locker_manager", tags=["Locker Manager"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/assign_item/{transaction_id}")
def assign_item(transaction_id: int, db: Session = Depends(get_db)):
    result = assign_item_to_locker(db, transaction_id)
    if result:
        return {"msg": "Item assigned to locker successfully"}
    return {"error": "Could not assign item to locker"}

@router.post("/open_locker/{locker_id}")
def open_locker_route(locker_id: int, db: Session = Depends(get_db)):
    success = open_locker(db, locker_id)
    if success:
        return {"msg": f"Locker {locker_id} opened successfully"}
    return {"error": "Unable to open locker"}
