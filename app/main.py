from fastapi import FastAPI
from app.routers import auth
from app.routers import owner



app = FastAPI(title="Barbershop API",)
app.include_router(auth.router)
app.include_router(owner.router)

