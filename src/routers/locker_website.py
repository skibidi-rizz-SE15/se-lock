from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import crud
from database import SessionLocal

router = APIRouter(prefix="/locker_website", tags=["Locker Website"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/check_transaction/{transaction_id}")
def check_transaction(transaction_id: int, db: Session = Depends(get_db)):
    trans = crud.get_transaction(db, transaction_id)
    if not trans:
        return {"error": "Transaction not found"}
    return {
        "start_date": trans.start_date,
        "transaction_id": trans.id,
        "borrower": trans.borrower,
        "lender": trans.lender,
        "state": trans.state,
        "locker_id": trans.locker_id
    }

@router.put("/change_transaction_state/{transaction_id}")
def change_transaction_state(transaction_id: int, new_state: int, db: Session = Depends(get_db)):
    trans = crud.update_transaction_state(db, transaction_id, new_state)
    if not trans:
        return {"error": "Transaction not found or cannot be updated"}
    return {"msg": f"Transaction {transaction_id} state updated to {new_state}"}
