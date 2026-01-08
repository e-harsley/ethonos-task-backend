from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class RegisterSchema(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    first_name: str = Field(..., min_length=1)
    last_name: str = Field(..., min_length=1)
    phone_number: Optional[str] = None


class LoginSchema(BaseModel):
    email: EmailStr
    password: str


class UserSchema(BaseModel):
    id: int
    email: str
    first_name: str
    last_name: str
    phone_number: Optional[str]
    date_joined: datetime
    is_active: bool

    class Config:
        from_attributes = True


class TokenSchema(BaseModel):
    access: str
    refresh: str


class MessageSchema(BaseModel):
    message: str
