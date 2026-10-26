from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class LoginIn(BaseModel):
    username: str
    password: str
    client: Literal["web", "ios", "android"] = "web"
    device_name: str | None = None


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str
    full_name: str
    role: str


class TokenOut(BaseModel):
    token: str
    user: UserOut


class BarberCreate(BaseModel):
    full_name: str = Field(min_length=2, max_length=100)
    phone: str | None = None
    username: str = Field(min_length=3, max_length=64)
    password: str = Field(min_length=8)
    role: Literal["master", "admin"] = "master"
    

class BarberOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str
    full_name: str
    phone: str | None
    role: str
    is_active: bool
    
class PasswordReset(BaseModel):
    new_password: str = Field(min_length=8)
    
    
class BarberCreated(BaseModel):
    code: int
    message: str
    barber: BarberOut

class BarberList(BaseModel):
    code: int
    message: str
    barbers: list[BarberOut]
    

class BarberUpdate(BaseModel):
    full_name: str | None = None
    phone: str | None = None