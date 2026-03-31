from fastapi import APIRouter, HTTPException, Depends
from app.schemas.pago_schema import PagoRequest, PagoResponse, ComprobantePago
from app.auth_utils import get_user_connection, get_current_user
from app.utils.pagos import validar_monto_pago
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

    # Validar que el monto del pago no exceda la deuda total (deuda + mora)
    estado_deuda = validar_monto_pago(
        cursor, pago.idcliente, pago.nprestamo, pago.monto
    )

    if not estado_deuda["puede_pagar"]:
        raise HTTPException(
            status_code=400,
            detail=(
                f"El monto del pago (${pago.monto}) excede la deuda total. "
                f"Deuda actual: ${estado_deuda['deuda_al_dia']:.2f}, "
                f"Mora: ${estado_deuda['mora_total']:.2f}, "
                f"Total deuda: ${estado_deuda['total_deuda']:.2f}"
            ),
        )

    # Extraer el momento actual completo
    offset = timezone(timedelta(hours=-4))  # Zona horaria de RD.
    ahora = datetime.now(offset)  # Tiempo Actual
    fecha_solo = ahora.date()  # estraer solo la fecha
    hora_full = ahora.replace(tzinfo=None)  # extraer solo la fecha

    # Consulta con 7 columnas para 7 valores
    query = """
        INSERT INTO handheldata (codigo, Cliente, Fecha, Hora, MontoPgdo, nprestamo, nusuario, cusuario)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
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
                pago.nprestamo,
                pago.idusuario,  # nusuario
                pago.usuario_nombre,  # cusuario
            ),
        )
        conn.commit()
        id_pago = cursor.lastrowid
        cursor.close()

        return {
            "idpago": id_pago if id_pago else None,
            "idnum": id_pago if id_pago else None,  # Añadir idnum para el recibo
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
def generar_recibo(
    recibo: ComprobantePago, current_user: dict = Depends(get_current_user)
):
    """
    Generar recibo de pago luego de realizar el envio
    """
    offset = timezone(timedelta(hours=-4))  # Zona horaria de RD.
    ahora = datetime.now(offset)
    ahora_str = ahora.strftime("%d-%m-%Y %H:%M")

    datos_recibo = {
        "nro_recibo": recibo.idnum,
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


@router.get("/recibo/reimpresion")
def reimprimir_recibo(
    current_user=Depends(get_current_user),
    conn: MySQLConnection = Depends(get_user_connection),
):
    """
    Listar todos los recibos realizados por el usuario actual
    """

    cursor = conn.cursor(dictionary=True)

    query = """
            SELECT h.idnum, h.cliente, h.MontoPgdo, h.cusuario, DATE_FORMAT(h.Hora, '%d/%m/%Y %H:%i') AS fecha
            FROM handheldata h
            JOIN ciadatabase.ciausers u ON h.nusuario = u.idusers
            WHERE u.idusers = %s 
            AND u.idcia = %s
            ORDER BY fecha DESC
            """
    cursor.execute(query, (current_user["idusuario"], current_user["idcia"]))
    pagos = cursor.fetchall()
    cursor.close()

    if not pagos:
        raise HTTPException(
            status_code=404, detail="No se encontraron pagos para este usuario"
        )

    return pagos
