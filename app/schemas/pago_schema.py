from pydantic import BaseModel, Field, field_validator
from typing import Optional
from decimal import Decimal


class PagoRequest(BaseModel):
    idcliente: int
    cliente_nombre: str = Field(min_length=3, max_length=45)
    monto: Decimal = Field(max_digits=10, decimal_places=2)
    nprestamo: int
    idusuario: int
    usuario_nombre: str

    @field_validator("cliente_nombre", "usuario_nombre", mode="before")
    @classmethod
    def strip_cliente(cls, v):
        return v.strip() if isinstance(v, str) else v

    @field_validator("monto", mode="before")
    @classmethod
    def validar_monto_positivo(cls, v):
        # Convertir a Decimal si no lo es
        if isinstance(v, str):
            v = Decimal(v)
        elif not isinstance(v, Decimal):
            v = Decimal(str(v))
        if v <= 0:
            raise ValueError("El monto del pago debe ser una cantidad mayor a cero.")
        return v


class PagoResponse(BaseModel):
    idpago: Optional[int] = None
    idnum: Optional[int] = None  # Añadir idnum para generar recibos
    message: str


class ComprobantePago(BaseModel):
    idnum: int
    cliente: str = Field(min_length=3, max_length=45)
    monto: Decimal = Field(max_digits=10, decimal_places=2)
    atendido_por: str = Field(min_length=3, max_length=45)
