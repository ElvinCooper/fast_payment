from pydantic import BaseModel


class LoginRequest(BaseModel):
    usuario: str
    password: str


class LoginResponse(BaseModel):
    idusuario: int
    usuario: str
    access_token: str
    token_type: str
    message: str
    user_db: str | None
    tipouser: str | None


class TokenRefreshResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
