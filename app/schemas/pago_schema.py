from pydantic import BaseModel, Field, field_validator
from typing import Optional
from decimal import Decimal

class PagoRequest(BaseModel):
    idcliente: int
    cliente_nombre: str = Field(..., max_length=45)
    monto: Decimal = Field(max_digits=10, decimal_places=2)
    idusuario: int
    usuario_nombre: str = Field(..., max_length=45)
    
    @field_validator('monto')
    @classmethod
    def validar_monto_positivo(cls, v: Decimal):
        if v <= 0:
            raise ValueError('El monto del pago debe ser una cantidad mayor a cero.')
        return v

class PagoResponse(BaseModel):
    idpago: Optional[int] = None
    message: str
