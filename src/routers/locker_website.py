from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import models, schemas, crud
from database import SessionLocal

router = APIRouter(prefix="/locker_website", tags=["Locker Website"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.put("/change_transaction_state/{transaction_id}")
def change_transaction_state(transaction_id: int, new_state: int, db: Session = Depends(get_db)):
    transaction = db.query(models.Transaction).filter(models.Transaction.id == transaction_id).first()
    if transaction:
        transaction.state = new_state
        db.commit()
        db.refresh(transaction)
        return {"message": "Transaction state updated"}
    return {"error": "Transaction not found"}

@router.get("/check_transaction/{transaction_id}")
def check_transaction(transaction_id: int, db: Session = Depends(get_db)):
    transaction = db.query(models.Transaction).filter(models.Transaction.id == transaction_id).first()
    return transaction if transaction else {"error": "Transaction not found"}
