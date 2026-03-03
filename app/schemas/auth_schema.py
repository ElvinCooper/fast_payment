from pydantic import BaseModel
from typing import Optional


class LoginRequest(BaseModel):
    usuario: str
    password: str


class LoginResponse(BaseModel):
    idusuario: int
    usuario: str
    access_token: str
    token_type: str
    message: str
