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
        if isinstance(v, str):
            v = Decimal(v)
        elif not isinstance(v, Decimal):
            v = Decimal(str(v))
        if v <= 0:
            raise ValueError("El monto del pago debe ser una cantidad mayor a cero.")
        return v


class PagoResponse(BaseModel):
    idpago: Optional[int] = None
    idnum: Optional[int] = None
    message: str


class ComprobantePago(BaseModel):
    idnum: int = Field(
        ...,
        description="Número único de pago/recibo generado al registrar el pago",
        json_schema_extra={"example": 106},
    )
    cliente: str = Field(
        ...,
        min_length=3,
        max_length=45,
        description="Nombre completo del cliente que realizó el pago",
        json_schema_extra={"example": "JUAN PEREZ GOMEZ"},
    )
    monto: Decimal = Field(
        ...,
        max_digits=10,
        decimal_places=2,
        description="Monto del pago realizado en RD$",
        json_schema_extra={"example": 2500.00},
    )
    atendido_por: str = Field(
        ...,
        min_length=3,
        max_length=45,
        description="Usuario o supervisor que atendió la transacción",
        json_schema_extra={"example": "SUPERVISOR"},
    )


class ReimpresionResponse(BaseModel):
    idnum: int
    cliente: str = Field(min_length=3, max_length=45)
    MontoPgdo: Decimal = Field(max_digits=10, decimal_places=2)
    cusuario: str = Field(min_length=3, max_length=45)
    fecha: Optional[str] = None
