"""/api/public/* — сайт и онлайн-запись. Эндпоинты — потом."""
from fastapi import APIRouter

router = APIRouter(prefix="/api/public", tags=["public"])
