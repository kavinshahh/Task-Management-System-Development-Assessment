from pydantic import BaseModel, EmailStr
from typing import Optional

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    first_name: str
    last_name: str
    password: str
    phone_number: int

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    username: str
    is_active: bool

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str


class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    priority: int

class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    priority: int
    complete: bool

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    username: str
    password: str
