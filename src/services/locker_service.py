# services/locker_service.py
from sqlalchemy.orm import Session
import crud

def open_locker(db: Session, locker_id: int) -> bool:
    """
    Attempt to 'open' a locker if it’s in a valid state.
    Return True if successful, False otherwise.
    """
    locker = crud.get_locker(db, locker_id)
    if locker and locker.state != 2:  # e.g. state=2 might be 'broken'
        # "Open" the locker in your real system
        # Possibly set state to 'occupied' or just do nothing if physically opened
        return True
    return False

def assign_item_to_locker(db: Session, transaction_id: int):
    """
    Mark the locker as occupied for the given transaction, if possible.
    """
    trans = crud.get_transaction(db, transaction_id)
    if trans and trans.locker_id:
        locker = crud.get_locker(db, trans.locker_id)
        if locker and locker.state == 0:  # 0=free
            crud.update_locker_state(db, locker.id, 1)  # 1=occupied
            return True
    return False
