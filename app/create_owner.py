"""Создать первого шефа. Запуск из папки backend: python -m app.create_owner"""
from getpass import getpass

from sqlalchemy import select

from app.db import SessionLocal
from app.models import User
from app.security import hash_password


def main():
    username = input("Логин шефа: ").strip()
    # getpass не показывает символы при вводе — это нормально
    password = getpass("Пароль (от 8 символов): ")
    if len(password) < 8:
        raise SystemExit("Пароль короче 8 символов")
    if getpass("Повторите пароль: ") != password:
        raise SystemExit("Пароли не совпадают")

    with SessionLocal() as db:
        if db.scalar(select(User).where(User.username == username)):
            raise SystemExit(f"Пользователь {username} уже есть")
        db.add(User(username=username, password_hash=hash_password(password), role="owner"))
        db.commit()
    print(f"Шеф {username} создан")


if __name__ == "__main__":
    main()
