from pydantic import BaseModel, EmailStr
from typing import List


class UserBase(BaseModel):
    password: str
    email: EmailStr

    class Config:
        from_attributes = True


class UserCreate(UserBase):
    password: str

    class Config:
        from_attributes = True


class UserSignin(BaseModel):
    email: str
    password: str

    class Config:
        from_attributes = True


class UserResponse(UserBase):
    transaction_list: List[dict]

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str

    class Config:
        from_attributes = True