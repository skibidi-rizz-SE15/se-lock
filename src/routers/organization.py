from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import crud, schemas
from database import SessionLocal

router = APIRouter(prefix="/organizations", tags=["Organizations"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=schemas.OrganizationOut)
def create_organization(org_in: schemas.OrganizationCreate, db: Session = Depends(get_db)):
    return crud.create_organization(db, org_in)

@router.get("/{org_id}", response_model=schemas.OrganizationOut)
def get_organization(org_id: int, db: Session = Depends(get_db)):
    org = crud.get_organization_by_id(db, org_id)
    if not org:
        return {"error": "Not found"}
    return org
