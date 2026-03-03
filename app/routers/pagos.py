from fastapi import APIRouter, Depends
from app.schemas.pago_schema import PagoRequest
from app.auth_utils import get_current_user

router = APIRouter(
    prefix="/api/v1/pagos", 
    tags=["Pagos"],
    dependencies=[Depends(get_current_user)]
)


@router.post("/")
def registrar_pago(pago: PagoRequest):
    """Registrar un pago (Protegido con JWT)"""
    # Aquí puedes agregar lógica para insertar en DB
    return {"message": "Pago registrado correctamente", "data": pago}
