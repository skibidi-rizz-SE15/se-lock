from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import crud, schemas
from database import SessionLocal
import models

router = APIRouter(prefix="/auth", tags=["Authentication"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/login")
def login(username: str, password: str, db: Session = Depends(get_db)):
    # Simplified example
    org = db.query(models.Organization).filter(models.Organization.username == username).first()
    if not org or org.password != password:
        raise HTTPException(status_code=400, detail="Incorrect username/password")
    return {"msg": "Login successful", "org_id": org.id}
