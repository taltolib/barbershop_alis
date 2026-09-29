from fastapi import FastAPI
from app.routers import auth



app = FastAPI(title="Barbershop API",)
app.include_router(auth.router)

