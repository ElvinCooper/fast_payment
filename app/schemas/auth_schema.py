from pydantic import BaseModel


class LoginRequest(BaseModel):
    usuario: str
    password: str


class LoginResponse(BaseModel):
    idusuario: int
    usuario: str
    message: str
