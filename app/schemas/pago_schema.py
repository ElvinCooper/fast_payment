from pydantic import BaseModel
from datetime import datetime

class PagoRequest(BaseModel):
    codigo_cliente: str
    monto_pagado: float
    nota: str
    cobrador: str
    fecha: datetime