from fastapi import FastAPI
from routers import organization, transaction, log, locker, locker_manager, locker_website

app = FastAPI()

app.include_router(organization.router)
app.include_router(transaction.router)
app.include_router(log.router)
app.include_router(locker.router)
app.include_router(locker_manager.router)
app.include_router(locker_website.router)

@app.get("/")
def root():
    return {"message": "Locker System API is running"}
