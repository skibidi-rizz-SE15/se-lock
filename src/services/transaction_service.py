from sqlalchemy.orm import Session
from crud import get_transaction, update_transaction_state

def validate_transaction_for_open(db: Session, transaction_id: int) -> bool:
    """
    Check if transaction is valid (state, date ranges, etc.) 
    before opening a locker.
    """
    trans = get_transaction(db, transaction_id)
    if not trans:
        return False
    # Example logic: check if transaction is "active"
    # Suppose 1 = ongoing state
    return trans.state == 1
