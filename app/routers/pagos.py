from fastapi import APIRouter, HTTPException, Depends
from app.schemas.pago_schema import PagoRequest, PagoResponse, ComprobantePago
from app.auth_utils import get_user_connection
from mysql.connector import MySQLConnection, Error
from datetime import datetime, timedelta, timezone
from fastapi.responses import StreamingResponse
from app.services.recibo_pdf import generar_recibo_termico
import uuid

router = APIRouter(
    prefix="/api/v1/pagos",
    tags=["Pagos"],
)


@router.post("/", response_model=PagoResponse)
def registrar_pago(
    pago: PagoRequest, conn: MySQLConnection = Depends(get_user_connection)
):
    """Registrar un nuevo pago en el sistema"""
    cursor = conn.cursor()

    """# Consultar cuánto debe el cliente actualmente
    query_deuda = "SELECT vprestamo FROM prestamo WHERE CODIGO = %s AND nprestamo = %s LIMIT 1"
    
    cursor.execute(query_deuda, (pago.idcliente, pago.nprestamo,))
    resultado = cursor.fetchone()
   
    if not resultado:
        raise HTTPException(status_code=404, detail="El cliente no tiene préstamos activos")
   
    deuda_actual = resultado['vprestamo']
   
    # Comparar el monto enviado con la deuda total
    if pago.monto > deuda_actual:
        raise HTTPException(status_code=400, detail=f"El monto ({pago.monto}) excede la deuda actual ({deuda_actual})")"""

    # Extraer el momento actual completo
    offset = timezone(timedelta(hours=-4))  # Zona horaria de RD.
    ahora = datetime.now(offset)  # Tiempo Actual
    fecha_solo = ahora.date()  # estraer solo la fecha
    hora_full = ahora.replace(tzinfo=None)  # extraer solo la fecha

    # Consulta con 7 columnas para 7 valores
    query = """
        INSERT INTO handheldata (codigo, Cliente, Fecha, Hora, MontoPgdo, nusuario, cusuario)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """

    try:
        cursor.execute(
            query,
            (
                pago.idcliente,  # codigo
                pago.cliente_nombre,  # Cliente
                fecha_solo,  # Fecha
                hora_full,  # Hora (Objeto datetime completo para campo DATETIME)
                pago.monto,  # MontoPgdo
                pago.idusuario,  # nusuario
                pago.usuario_nombre,  # cusuario
            ),
        )
        conn.commit()
        id_pago = cursor.lastrowid
        cursor.close()

        return {
            "idpago": id_pago if id_pago else None,
            "message": "Pago registrado exitosamente",
        }

    except Error as e:
        conn.rollback()
        cursor.close()
        raise HTTPException(
            status_code=500,
            detail=f"Error al registrar el pago en la tabla handheldata: {str(e)}",
        )


@router.post("/recibo")
def generar_recibo(recibo: ComprobantePago):
    """
    Generar recibo de pago luego de realizar el envio
    """
    offset = timezone(timedelta(hours=-4))  # Zona horaria de RD.
    ahora = datetime.now(offset)
    ahora_str = ahora.strftime("%d-%m-%Y %H:%M")

    datos_recibo = {
        "nro_recibo": str(uuid.uuid4())[:8],
        "cliente": recibo.cliente,
        "fecha": ahora_str,
        "monto": recibo.monto,
        "atendido_por": recibo.atendido_por,
    }

    try:
        comprobante = generar_recibo_termico(datos_recibo)
        fecha_filename = ahora.strftime("%Y%m%d")
        return StreamingResponse(
            comprobante,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=recibo_{datos_recibo['nro_recibo']}_{fecha_filename}.pdf"
            },
        )
    except Exception as err:
        raise HTTPException(
            status_code=500,
            detail=f"Error al generar comprobante de pago: {err}",
        )
