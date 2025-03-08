from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import crud, schemas
from database import SessionLocal

router = APIRouter(prefix="/logs", tags=["Logs"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=schemas.LogOut)
def create_log(log_in: schemas.LogCreate, db: Session = Depends(get_db)):
    return crud.create_log(db, log_in)

@router.get("/{log_id}", response_model=schemas.LogOut)
def get_log(log_id: int, db: Session = Depends(get_db)):
    db_log = crud.get_log(db, log_id)
    if not db_log:
        return {"error": "Log not found"}
    return db_log
