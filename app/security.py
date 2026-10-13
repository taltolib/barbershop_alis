import hashlib                       # sha256 для токена
import secrets                       # безопасный генератор случайных токенов
from datetime import timedelta       # «15 дней»

from pwdlib import PasswordHash      # Argon2 для паролей

IDLE_TTL = timedelta(days=15)         # сессия живёт 15 дней с последнего запроса
_hasher = PasswordHash.recommended()  


def verify_password(password: str, password_hash: str) -> bool:
    return _hasher.verify(password, password_hash)

def hash_password(password: str) -> str:
    return _hasher.hash(password)


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()

def generate_token() -> str:
    return secrets.token_urlsafe(32)

