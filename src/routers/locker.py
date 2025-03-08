from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import crud, schemas
from database import SessionLocal

router = APIRouter(prefix="/lockers", tags=["Lockers"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=schemas.LockerOut)
def create_locker(locker_in: schemas.LockerCreate, db: Session = Depends(get_db)):
    return crud.create_locker(db, locker_in)

@router.put("/{locker_id}/change_state")
def change_locker_state(locker_id: int, new_state: int, db: Session = Depends(get_db)):
    locker = crud.update_locker_state(db, locker_id, new_state)
    if not locker:
        return {"error": "Locker not found"}
    return {"msg": f"Locker {locker_id} updated to state {new_state}"}
