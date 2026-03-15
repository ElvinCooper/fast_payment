from pydantic import BaseModel, Field, field_validator, BeforeValidator
from pydantic_core import PydanticCustomError
from typing import Optional, Any, Annotated
from decimal import Decimal
from datetime import datetime


# funcion reutilizable para validar que el campo sea string sin numeros
def nombre_sin_numeros(valor: Any) -> str:
    if valor is None:
        raise ValueError("El CLIENTE no puede ser nulo")
    if isinstance(valor, str) and any(char.isdigit() for char in valor):
        raise PydanticCustomError("str_type", "El nombre no debe contener numeros.", {})
    return valor


NombreSinNumeros = Annotated[str, BeforeValidator(nombre_sin_numeros)]


class ParamNombre(BaseModel):
    CLIENTE: NombreSinNumeros = Field(
        ..., description="Nombre o parte del nombre del cliente a buscar"
    )


class ClientBase(BaseModel):
    idcliente: int
    CLIENTE: str


class ClienteResponse(BaseModel):
    idcliente: int
    CLIENTE: Optional[NombreSinNumeros]
    nprestamo: int
    vprestamo: Decimal = Field(max_digits=10, decimal_places=2)
    FECHAP: Optional[str] = None
    fechav: Optional[str] = None
    cel: Optional[str] = None
    estado_cuota: Optional[str] = None
    cantidad_cutas: int
    vpendiente: Decimal = Field(max_digits=10, decimal_places=2)

    @field_validator("CLIENTE", mode="before")
    @classmethod
    def strip_cliente(cls, v):
        if v is None:
            return v
        return v.strip() if isinstance(v, str) else v


class CuotaVencidaResponse(BaseModel):
    NPRESTAMO: int
    CODIGO: int
    CLIENTE: str
    FECHAP: datetime
    fechav: datetime
    cel: str
    ncuotas: int
    vpendiente: Decimal = Field(max_digits=10, decimal_places=2)
    estado_cuota: str = "con cuota vencida"  # Campo por default
