from pydantic import BaseModel

class OrganizationCreate(BaseModel):
    username: str
    password: str

class TransactionCreate(BaseModel):
    borrower: int
    lender: int
    start_date: int
    end_date: int
    state: int

class LogCreate(BaseModel):
    action: int
    log_id: int
    person: int
    time: int

class LockerCreate(BaseModel):
    state: int
