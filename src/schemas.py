# schemas.py
from pydantic import BaseModel
from typing import Optional

# ----- Organization -----
class OrganizationBase(BaseModel):
    username: str

class OrganizationCreate(OrganizationBase):
    password: str

class OrganizationOut(OrganizationBase):
    id: int
    class Config:
        orm_mode = True

# ----- Transaction -----
class TransactionBase(BaseModel):
    borrower: int
    lender: int
    start_date: int
    end_date: int
    state: int
    locker_id: Optional[int]

class TransactionCreate(TransactionBase):
    pass

class TransactionOut(TransactionBase):
    id: int
    class Config:
        orm_mode = True

# ----- Log -----
class LogBase(BaseModel):
    action: int
    person: int
    time: int
    transaction_id: Optional[int]

class LogCreate(LogBase):
    pass

class LogOut(LogBase):
    id: int
    class Config:
        orm_mode = True

# ----- Locker -----
class LockerBase(BaseModel):
    state: int

class LockerCreate(LockerBase):
    pass

class LockerOut(LockerBase):
    id: int
    class Config:
        orm_mode = True
