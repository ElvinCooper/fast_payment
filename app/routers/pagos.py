from fastapi import APIRouter
from app.schemas.pago_schema import PagoRequest

router = APIRouter(prefix="/pagos", tags=["Pagos"])


@router.post("/")
def registrar_pago(pago: PagoRequest):
    # Aquí puedes agregar lógica para insertar en DB
    return {"message": "Pago registrado correctamente", "data": pago}
