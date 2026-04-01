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
    empresa: str | None
    tipouser: str | None
    db_name: str | None = None  # NUEVO: nombre de BD en el token
    empresas: list[dict] | None = None  # NUEVO: lista de empresas
    requires_selection: bool = False  # NUEVO: flag para frontend


class TokenRefreshResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class SwitchTenantRequest(BaseModel):
    empresa_id: int


class SwitchTenantResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    db_name: str
    empresa: str
    message: str
    empresas: list[dict] | None = None
    requires_selection: bool = False
