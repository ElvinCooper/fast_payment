from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


 
class UserDBRoutingResponse(BaseModel):
    idusuario: int
    usuario: str    


class UserDBRoutingUpdate(BaseModel):
    idusuario: int    
    database: str | None = Field(..., max_length=100)
    clave:   str | None   = Field(..., max_length=30)