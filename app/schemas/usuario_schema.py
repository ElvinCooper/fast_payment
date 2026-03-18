from pydantic import BaseModel


class UserBase(BaseModel):
    idusuario: int
    usuario: str    
