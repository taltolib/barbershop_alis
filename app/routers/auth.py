from fastapi import APIRouter
from app.schemas import LoginIn


router = APIRouter(prefix="/api/auth",)


@router.post("/login")
async def login(data : LoginIn):
    return {
        "message": "Login endpoint",
        "data": data.username
    }
