from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import models, schemas, crud
from database import SessionLocal

router = APIRouter(prefix="/organizations", tags=["Organizations"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=schemas.OrganizationCreate)
def create_organization(org: schemas.OrganizationCreate, db: Session = Depends(get_db)):
    return crud.create_organization(db, org)
