from fastapi import FastAPI
from database import Base, engine
from routers import organization, transaction, log, locker, locker_manager, locker_website
from routers import auth 


Base.metadata.create_all(bind=engine)

app = FastAPI(title="Locker System API")

app.include_router(organization.router)
app.include_router(transaction.router)
app.include_router(log.router)
app.include_router(locker.router)
app.include_router(locker_manager.router)
app.include_router(locker_website.router)
app.include_router(auth.router)

@app.get("/")
def root():
    return {"message": "Locker System API is running"}
