from pydantic import BaseModel, Field


class UserDBRoutingResponse(BaseModel):
    idusuario: int
    usuario: str


class UserDBRoutingUpdate(BaseModel):
    idusuario: int
    database: str | None = Field(default=None, max_length=100)
    clave: str | None = Field(default=None, max_length=30)


class UserCIAUpdate(BaseModel):
    idusers: int
    clave: str | None = Field(default=None, max_length=30, description="Nueva clave")
    estatus: int | None = Field(default=None, description="1=activo, 0=inactivo")
    tipouser: str | None = Field(
        default=None, max_length=20, description="admin, standard"
    )


class DatabasesResponse(BaseModel):
    databases: list[str]
