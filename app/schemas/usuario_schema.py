from pydantic import BaseModel


class UserBase(BaseModel):
    idusuario: int
    usuario: str   
    db_asignada: str | None =None
    empresa:  str | None = None
    tipouser: str | None = None
    empresas: list[dict] | None = None 
    requires_selection: bool = False 
