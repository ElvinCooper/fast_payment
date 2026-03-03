from pydantic import BaseModel, Field
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
    vprestamo: Decimal = Field(max_digits=10, decimal_places=2)
    fecha: Optional[str] = None
