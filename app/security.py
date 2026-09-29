"""Пароли, токены сессий и текущий пользователь. Только стандартная библиотека Python."""
import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone

from fastapi import Cookie, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import SECRET_KEY, SESSION_COOKIE, SESSION_DAYS
from app.db import get_db
from app.models import User, UserSession

# scrypt — медленный хэш с солью: перебор паролей по украденной базе становится дорогим.
# Обычный sha256 для паролей не годится: он слишком быстрый и без соли.
SCRYPT_N, SCRYPT_R, SCRYPT_P = 2**14, 8, 1


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.scrypt(password.encode(), salt=salt, n=SCRYPT_N, r=SCRYPT_R, p=SCRYPT_P)
    # Параметры храним в строке, чтобы потом можно было их усилить, не ломая старые пароли
    return f"scrypt${SCRYPT_N}${SCRYPT_R}${SCRYPT_P}${salt.hex()}${digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        _, n, r, p, salt_hex, digest_hex = stored.split("$")
        digest = hashlib.scrypt(
            password.encode(), salt=bytes.fromhex(salt_hex), n=int(n), r=int(r), p=int(p)
        )
    except ValueError:
        return False
    return hmac.compare_digest(digest.hex(), digest_hex)


# Проверяем пароль и для несуществующего логина, чтобы по времени ответа
# нельзя было понять, есть такой пользователь или нет
DUMMY_HASH = hash_password("dummy-password")


def hash_token(token: str) -> str:
    """В базе лежит только HMAC токена: по утёкшей таблице sessions войти нельзя."""
    return hmac.new(SECRET_KEY.encode(), token.encode(), hashlib.sha256).hexdigest()


def create_session(db: Session, user: User, ip: str | None) -> str:
    """Создаёт строку в sessions и возвращает токен для куки."""
    token = secrets.token_urlsafe(32)
    db.add(
        UserSession(
            user_id=user.id,
            token_hash=hash_token(token),
            ip=ip,
            expires_at=datetime.now(timezone.utc) + timedelta(days=SESSION_DAYS),
        )
    )
    return token


def get_current_user(
    token: str | None = Cookie(None, alias=SESSION_COOKIE),
    db: Session = Depends(get_db),
) -> User:
    """Зависимость: пользователь по куке сессии, иначе 401."""
    if not token:
        raise HTTPException(401, "Не авторизован")
    session = db.scalar(
        select(UserSession).where(
            UserSession.token_hash == hash_token(token),
            UserSession.expires_at > datetime.now(timezone.utc),
        )
    )
    if session is None or not session.user.is_active:
        raise HTTPException(401, "Не авторизован")
    return session.user
