from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException 
from fastapi.security import HTTPAuthorizationCredentials
from app.errors import Err, api_error
from app.schemas import LoginIn, TokenOut, UserOut
from app.models import User, UserSession
from app.db import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select , delete
from app.security import IDLE_TTL, generate_token, hash_token, verify_password
from app.deps import current_user, bearer


router = APIRouter(
    prefix="/api/auth",
)


@router.post("/login", response_model=TokenOut)
async def login(data: LoginIn, db: AsyncSession = Depends(get_session)):
    
    result = await db.execute(select(User).where(User.username == data.username))
    users = result.scalar_one_or_none()
    if not users:
        raise api_error(404, Err.USER_NOT_FOUND, "Пользователь не найден")

    if users is None or not verify_password(data.password, users.password_hash):
        raise api_error(401, Err.BAD_CREDENTIALS, "Неверный логин или пароль")
    
    if not users.is_active:
        raise api_error(403, Err.ACCOUNT_DISABLED, "Аккаунт отключён")
    
    token = generate_token()    
    session = UserSession(
        user_id=users.id, 
        client=data.client,
        device_name=data.device_name,
        token_hash=hash_token(token),
        expires_at=datetime.now(timezone.utc) + IDLE_TTL,
        )

    db.add(session)
    await db.commit()

    return {"code": 200, "token": token, "user": users}


@router.post("/logout")
async def logout(creds: HTTPAuthorizationCredentials = Depends(bearer), user: User = Depends(current_user),db: AsyncSession = Depends(get_session)):
    await db.execute(
        delete(UserSession).where(UserSession.token_hash == hash_token(creds.credentials))
    )
    await db.commit()
    
    return { "code ":200,"message": "Logout successful"}
    
    
@router.get("/me", response_model=UserOut)
async def me(user: User = Depends(current_user)):
    return user

