from sqlalchemy.orm import Session
import models, schemas

def create_organization(db: Session, org: schemas.OrganizationCreate):
    db_org = models.Organization(username=org.username, password=org.password)
    db.add(db_org)
    db.commit()
    db.refresh(db_org)
    return db_org

def create_transaction(db: Session, transaction: schemas.TransactionCreate):
    db_trans = models.Transaction(**transaction.dict())
    db.add(db_trans)
    db.commit()
    db.refresh(db_trans)
    return db_trans
                                                                                                                                                                                                                               # crud.py
from sqlalchemy.orm import Session
import models, schemas

# ---------- Organization ----------
def create_organization(db: Session, org: schemas.OrganizationCreate):
    db_org = models.Organization(
        username=org.username,
        password=org.password
    )
    db.add(db_org)
    db.commit()
    db.refresh(db_org)
    return db_org

def get_organization_by_id(db: Session, org_id: int):
    return db.query(models.Organization).filter(models.Organization.id == org_id).first()

# ---------- Transaction ----------
def create_transaction(db: Session, transaction: schemas.TransactionCreate):
    db_trans = models.Transaction(**transaction.dict())
    db.add(db_trans)
    db.commit()
    db.refresh(db_trans)
    return db_trans

def get_transaction(db: Session, transaction_id: int):
    return db.query(models.Transaction).filter(models.Transaction.id == transaction_id).first()

def update_transaction_state(db: Session, transaction_id: int, new_state: int):
    db_trans = get_transaction(db, transaction_id)
    if db_trans:
        db_trans.state = new_state
        db.commit()
        db.refresh(db_trans)
    return db_trans

# ---------- Log ----------
def create_log(db: Session, log_in: schemas.LogCreate):
    db_log = models.Log(**log_in.dict())
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log

def get_log(db: Session, log_id: int):
    return db.query(models.Log).filter(models.Log.id == log_id).first()

# ---------- Locker ----------
def create_locker(db: Session, locker_in: schemas.LockerCreate):
    db_locker = models.Locker(**locker_in.dict())
    db.add(db_locker)
    db.commit()
    db.refresh(db_locker)
    return db_locker

def get_locker(db: Session, locker_id: int):
    return db.query(models.Locker).filter(models.Locker.id == locker_id).first()

def update_locker_state(db: Session, locker_id: int, new_state: int):
    locker = get_locker(db, locker_id)
    if locker:
        locker.state = new_state
        db.commit()
        db.refresh(locker)
    return locker
                                                                                                     