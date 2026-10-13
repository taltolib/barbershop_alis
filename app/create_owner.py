import asyncio
import sys

from app.db import async_session
from app.models import User
from app.security import hash_password


async def main(username: str, password: str, full_name: str) -> None:
    async with async_session() as db:
        db.add(User(
            username=username,
            password_hash=hash_password(password),
            full_name=full_name,
            role="owner",
        ))
        await db.commit()
    print(f"Владелец '{username}' создан")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit('Использование: python -m app.create_owner логин пароль "Имя Фамилия"')
    asyncio.run(main(*sys.argv[1:]))
    
# Это нужно чтобы создавать владельца через командную строку,для барбершопа: