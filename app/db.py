"""Подключение к базе, базовый класс таблиц и зависимость get_db."""
from datetime import datetime

from sqlalchemy import DateTime, create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import DATABASE_URL

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    # Все поля datetime храним с часовым поясом (timestamptz в PostgreSQL)
    type_annotation_map = {datetime: DateTime(timezone=True)}


def get_db():
    """Одна сессия базы на один запрос; после ответа закрывается."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
