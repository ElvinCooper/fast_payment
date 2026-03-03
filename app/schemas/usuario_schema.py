from pydantic import BaseModel, Field


class UserBase(BaseModel):
    idusuario: int
    usuario: str    
