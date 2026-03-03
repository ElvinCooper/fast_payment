from pydantic import BaseModel
from typing import Optional
from decimal import Decimal
from datetime import datetime


class ClientBase(BaseModel):
    idcliente: int
    CLIENTE: str


class ClienteResponse(BaseModel):
    idcliente: int
    CLIENTE: str
    nprestamo: int
    vprestamo: float
    fecha: Optional[str] = None
