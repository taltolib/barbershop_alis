import asyncio

from sqlalchemy import text

from app.db import engine


async def main():
    async with engine.connect() as conn:
        version = (await conn.execute(text("select version()"))).scalar()
    print("Подключение работает:", version)
    await engine.dispose()


asyncio.run(main())

# чтобы запустить вот команда python -m app.check_db