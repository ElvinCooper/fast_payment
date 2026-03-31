from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.schemas.pago_schema import (
    PagoRequest,
    PagoResponse,
    ComprobantePago,
    ReimpresionResponse,
)
from app.auth_utils import get_user_connection, get_current_user
from app.utils.pagos import validar_monto_pago
from mysql.connector import MySQLConnection, Error
from datetime import datetime, timedelta, timezone
from fastapi.responses import StreamingResponse
from app.services.recibo_pdf import generar_recibo_termico

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


@router.post(
    "/recibo",
    responses={
        200: {
            "content": {"application/pdf": {}},
            "description": "Recibo de pago en formato PDF (tamaño térmico 70x120mm)",
        },
        500: {"description": "Error al generar el comprobante de pago"},
    },
)
def generar_recibo(
    recibo: ComprobantePago, current_user: dict = Depends(get_current_user)
):
    """
    Genera un recibo de pago en formato PDF térmico.

    Genera un comprobante PDF con la información del pago realizado.
    El PDF incluye: encabezado de la empresa, número de recibo, datos del cliente,
    monto pagado y usuario que atendió la transacción.

    - **idnum**: Número único de pago/recibo
    - **cliente**: Nombre del cliente que realizó el pago
    - **monto**: Monto pagado en RD$
    - **atendido_por**: Usuario que procesó el pago

    Returns: Archivo PDF con el recibo (Content-Type: application/pdf)
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


@router.get("/historial", response_model=List[ReimpresionResponse])
def historial_pagos(
    current_user=Depends(get_current_user),
    conn: MySQLConnection = Depends(get_user_connection),
):
    """
    Listar todos los pagos realizados por el usuario actual
    """
    cursor = conn.cursor(dictionary=True)

    if current_user["tipouser"] == "admin":
        query = """
            SELECT h.idnum, h.cliente, h.MontoPgdo, h.cusuario, DATE_FORMAT(h.Hora, '%d/%m/%Y %H:%i') AS fecha
            FROM handheldata h
            ORDER BY h.Hora DESC
        """
        cursor.execute(query)
    else:
        query = """
            SELECT h.idnum, h.cliente, h.MontoPgdo, h.cusuario, DATE_FORMAT(h.Hora, '%d/%m/%Y %H:%i') AS fecha
            FROM handheldata h
            WHERE h.nusuario = %s
            ORDER BY h.Hora DESC
        """
        cursor.execute(query, (current_user["idusuario"],))

    pagos = cursor.fetchall()
    cursor.close()

    if not pagos:
        raise HTTPException(
            status_code=404, detail="No se encontraron pagos para este usuario"
        )

    return pagos
