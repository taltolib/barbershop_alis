from datetime import datetime, timezone

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.errors import Err, api_error
from app.models import User, UserSession
from app.security import IDLE_TTL, hash_token

bearer = HTTPBearer(auto_error=False)


async def current_user(
    creds: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: AsyncSession = Depends(get_session),
) -> User:
    
    if creds is None:
        raise api_error(401, Err.SESSION_INVALID, "Нужен вход")

    now = datetime.now(timezone.utc)
    result = await db.execute(
        select(UserSession, User)
        .join(User, User.id == UserSession.user_id)
        .where(
            UserSession.token_hash == hash_token(creds.credentials),
            UserSession.revoked_at.is_(None),
            UserSession.expires_at > now,
            User.is_active.is_(True),
        )
    )
    row = result.first()
    if row is None:
        raise api_error(401, Err.SESSION_INVALID, "Сессия недействительна")

    session, user = row
    session.last_used_at = now
    session.expires_at = now + IDLE_TTL
    await db.commit()
    return user


def require_roles(*roles: str):
    async def checker(user: User = Depends(current_user)) -> User:
        if user.role not in roles:
            raise api_error(403, Err.FORBIDDEN, "Недостаточно прав")
        return user
    return checker


require_owner = require_roles("owner")