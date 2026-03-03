from fastapi import APIRouter, HTTPException, Depends, Query
from app.schemas.cliente_schema import ClienteResponse, ClientBase
from typing import List
from app.database import get_connection
from mysql.connector import MySQLConnection
from datetime import datetime

router = APIRouter(prefix="/api/v1/clientes", tags=["Clientes"])


@router.get("/buscar", response_model=List[ClienteResponse], summary="Buscar clientes por nombre (LIKE)",)
def buscar_clientes_por_nombre(nombre: str = Query(..., description="Nombre o parte del nombre del cliente a buscar"),
    conn: MySQLConnection = Depends(get_connection),):
    """Buscar clientes por nombre"""
    cursor = conn.cursor(dictionary=True)

    query = """
       SELECT CL.idcliente, CL.CLIENTE, PR.nprestamo, PR.vprestamo 
       FROM cliente CL
       JOIN prestamo PR ON CL.idcliente = PR.CODIGO
       WHERE CL.CLIENTE LIKE %s
       LIMIT 20
    """

    cursor.execute(query, (f"%{nombre}%",))
    resultados = cursor.fetchall()
    cursor.close()

    if not resultados:
        raise HTTPException(
            status_code=404, detail="No se encontraron clientes con el nombre indicado"
        )

    now = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    for r in resultados:
        r["fecha"] = now

    return resultados



@router.get("/{codigo}", response_model=List[ClienteResponse])
def obtener_clientes(codigo: str, conn: MySQLConnection = Depends(get_connection)):
    """Obtener cliente por su codigo"""
    cursor = conn.cursor(dictionary=True)

    query = f"""SELECT CL.idcliente, CL.CLIENTE, PR.nprestamo, PR.vprestamo FROM cliente CL
            JOIN prestamo PR ON CL.idcliente = PR.CODIGO
            WHERE CL.idcliente = %s;
         """
    cursor.execute(query, (codigo,))
    results = cursor.fetchall()
    cursor.close()

    if not results:
        raise HTTPException(
            status_code=404, detail="No se encontraron clientes o prestamos"
        )

    now = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    for r in results:
        r["fecha"] = now

    return results
