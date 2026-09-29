"""Что приходит в запросах и уходит в ответах (Pydantic)."""
from pydantic import BaseModel, ConfigDict, Field


class LoginIn(BaseModel):
    username: str
    password: str


class PasswordIn(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8)


class Me(BaseModel):
    # from_attributes: можно вернуть объект User из базы, Pydantic возьмёт из него поля
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    role: str
    barber: dict | None = None  # заполним, когда появится таблица barbers


class OkOut(BaseModel):
    ok: bool = True
