from fastapi import APIRouter, HTTPException, Depends
from app.schemas.pago_schema import PagoRequest, PagoResponse
from app.database import get_connection
from app.auth_utils import get_current_user
from mysql.connector import MySQLConnection, Error
from datetime import datetime

router = APIRouter(
    prefix="/api/v1/pagos", 
    tags=["Pagos"],
    dependencies=[Depends(get_current_user)]
)


@router.post("/", response_model=PagoResponse)
def registrar_pago(pago: PagoRequest, conn: MySQLConnection = Depends(get_connection)):
    """Registrar un nuevo pago en la tabla handheldata (Fecha y Hora automáticas)"""
    cursor = conn.cursor()
    
    '''# Consultar cuánto debe el cliente actualmente
    query_deuda = "SELECT vprestamo FROM prestamo WHERE CODIGO = %s LIMIT 1"
    cursor.execute(query_deuda, (pago.idcliente,))
    resultado = cursor.fetchone()
   
    if not resultado:
        raise HTTPException(status_code=404, detail="El cliente no tiene préstamos activos")
   
    deuda_actual = resultado['vprestamo']
   
    # Comparar el monto enviado con la deuda real
    if pago.monto > deuda_actual:
        raise HTTPException(status_code=400, detail=f"El monto ({pago.monto}) excede la deuda actual ({deuda_actual})")'''
    
    
    # Extraer el momento actual completo
    ahora = datetime.now()
    fecha_solo = ahora.date()            # Solo la fecha: YYYY-MM-DD
    hora_full = ahora                    # El objeto datetime completo (Fecha + Hora)
    
    # Consulta con 7 columnas para 7 valores
    query = """
        INSERT INTO handheldata (codigo, Cliente, Fecha, Hora, MontoPgdo, nusuario, cusuario)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    
    try:
        cursor.execute(query, (
            pago.idcliente,      # codigo
            pago.cliente_nombre, # Cliente
            fecha_solo,          # Fecha
            hora_full,           # Hora (Objeto datetime completo para campo DATETIME)
            pago.monto,          # MontoPgdo
            pago.idusuario,      # nusuario
            #pago.nota,           # nota   
            pago.usuario_nombre  # cusuario
        ))
        conn.commit()
        id_pago = cursor.lastrowid
        cursor.close()
        
        return {
            "idpago": id_pago if id_pago else None,
            "message": "Pago registrado exitosamente"
        }
        
    except Error as e:
        conn.rollback()
        cursor.close()
        raise HTTPException(
            status_code=500, 
            detail=f"Error al registrar el pago en la tabla handheldata: {str(e)}"
        )
