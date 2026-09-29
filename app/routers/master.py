"""/api/master/* — кабинет мастера. Эндпоинты — потом."""
from fastapi import APIRouter

router = APIRouter(prefix="/api/master", tags=["master"])
