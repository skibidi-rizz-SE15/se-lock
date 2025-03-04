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
                                                                                                                                                                                                                                                                                                                                    