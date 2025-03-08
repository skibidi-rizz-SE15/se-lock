from sqlalchemy.orm import Session
import crud, schemas

def send_log(db: Session, action: int, person: int, time: int, transaction_id: int):
    # Basic log creation
    log_data = schemas.LogCreate(
        action=action,
        person=person,
        time=time,
        transaction_id=transaction_id
    )
    return crud.create_log(db, log_data)
