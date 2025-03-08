from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import crud, schemas
from database import SessionLocal
from services.transaction_service import validate_transaction_for_open

router = APIRouter(prefix="/transactions", tags=["Transactions"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=schemas.TransactionOut)
def create_transaction(trans_in: schemas.TransactionCreate, db: Session = Depends(get_db)):
    return crud.create_transaction(db, trans_in)

@router.get("/{transaction_id}", response_model=schemas.TransactionOut)
def read_transaction(transaction_id: int, db: Session = Depends(get_db)):
    trans = crud.get_transaction(db, transaction_id)
    if not trans:
        return {"error": "Transaction not found"}
    return trans

@router.put("/{transaction_id}/change_state")
def change_transaction_state(transaction_id: int, new_state: int, db: Session = Depends(get_db)):
    trans = crud.update_transaction_state(db, transaction_id, new_state)
    if not trans:
        return {"error": "Cannot update. Transaction not found."}
    return {"msg": f"State updated to {new_state}"}

@router.get("/{transaction_id}/validate")
def validate_for_open(transaction_id: int, db: Session = Depends(get_db)):
    is_valid = validate_transaction_for_open(db, transaction_id)
    return {"valid": is_valid}
