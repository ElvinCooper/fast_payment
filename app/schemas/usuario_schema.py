from pydantic import BaseModel


class UserBase(BaseModel):
    idusuario: int
    usuario: str
    db_asignada: str | None = None
    empresa: str | None = None
    tipouser: str | None = None
    empresas: list[dict] | None = None
    requires_selection: bool = False


class UserTipos(BaseModel):
    tipos_usuario: list[str]


class SystemUsersResponse(BaseModel):
    idusuario: int
    usuario: str
    tipouser: str


class UserEmprresaResponse(BaseModel):
    idcia: int
    ciadescription: str
    descdb: str
