"""/api/owner/* — админка шефа."""
from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from sqlalchemy import select , delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.deps import require_owner
from app.errors import Err, api_error
from app.models import User
from app.schemas import BarberCreate, BarberOut
from app.security import hash_password
from app.models import UserSession


router = APIRouter(
    prefix="/api/owner",
    tags=["owner"],
    dependencies=[Depends(require_owner)],
)

async def revoke_all_sessions(db: AsyncSession, user_id: int) -> None:
    await db.execute(delete(UserSession).where(UserSession.user_id == user_id))
    

@router.post("/add/barber", response_model=BarberOut)
async def add_barber(data: BarberCreate, db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(User).where(User.username == data.username))
    if result.scalar_one_or_none():
        raise api_error(409, Err.USERNAME_TAKEN, "Такой логин уже занят")

    new_barber = User(
        full_name=data.full_name,
        phone=data.phone,
        username=data.username,
        password_hash=hash_password(data.password),
        role=data.role,
    )
    db.add(new_barber)
    await db.commit()

    return {"code": 200, "message": "Барбер успешно добавлен", "barber": new_barber}


@router.get("/barbers", response_model=list[BarberOut])
async def list_barbers(db: AsyncSession = Depends(get_session)):
    result = await db.execute(
        select(User).where(User.role.in_(["master", "admin"])).order_by(User.id)
    )
    
    return {"code": 200, "message": "Барберы успешно получены", "barbers": result.scalars().all()}

@router.delete("/barbers/{barber_id}/sessions")
async def force_logout_barber(barber_id: int, db: AsyncSession = Depends(get_session)):
    barber = await db.get(User, barber_id)
    if barber is None:
        raise api_error(404, Err.USER_NOT_FOUND, "Барбер не найден")

    await revoke_all_sessions(db, barber_id)
    await db.commit()
    return {"code": 200, "message": "Барбер успешно разлогинен"}


@router.post("/barbers/{barber_id}/dismiss")
async def dismiss_barber(barber_id: int, db: AsyncSession = Depends(get_session)):
    barber = await db.get(User, barber_id)
    if barber is None:
        raise api_error(404, Err.USER_NOT_FOUND, "Барбер не найден")
    if barber.role == "owner":
        raise api_error(403, Err.FORBIDDEN, "Нельзя уволить владельца")
    if not barber.is_active:
        raise api_error(409, Err.ALREADY_DISMISSED, "Барбер уже уволен")

    barber.is_active = False
    barber.dismissed_at = datetime.now(timezone.utc)
    await revoke_all_sessions(db, barber_id)
    await db.commit()
    return {"code": 200, "message": "Барбер успешно уволен"}