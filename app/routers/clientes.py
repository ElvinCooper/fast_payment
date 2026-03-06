from fastapi import APIRouter, HTTPException, Depends, Query
from app.schemas.cliente_schema import ClienteResponse, ParamNombre, NombreSinNumeros
from typing import List
from app.database import get_connection
from app.auth_utils import get_current_user
from mysql.connector import MySQLConnection
from datetime import datetime

router = APIRouter(
    prefix="/api/v1/clientes",
    tags=["Clientes"],
    dependencies=[Depends(get_current_user)],
)


@router.get("/", response_model=List[ClienteResponse])
def obtener_clientes(conn: MySQLConnection = Depends(get_connection)):
    """Obtener todos los clientes con prestamos activos"""
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT CL.idcliente, CL.CLIENTE, PR.nprestamo, PR.vprestamo 
        FROM cliente CL
        JOIN prestamo PR ON CL.idcliente = PR.CODIGO        
    """
    cursor.execute(
        query,
    )
    results = cursor.fetchall()
    cursor.close()

    if not results:
        raise HTTPException(
            status_code=404, detail="No se encontraron clientes con prestamos activos"
        )

    now = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    for r in results:
        r["fecha"] = now

    return results


@router.get(
    "/buscar",
    response_model=List[ClienteResponse],
)
def buscar_clientes_por_nombre(
    params: ParamNombre = Depends(),
    conn: MySQLConnection = Depends(get_connection),
):
    """Buscar clientes por nombre (Protegido con JWT)"""
    cursor = conn.cursor(dictionary=True)

    query = """
       SELECT CL.idcliente, CL.CLIENTE, PR.nprestamo, PR.vprestamo 
       FROM cliente CL
       JOIN prestamo PR ON CL.idcliente = PR.CODIGO
       WHERE CL.CLIENTE LIKE %s AND CL.CLIENTE IS NOT NULL
       LIMIT 20
    """

    cursor.execute(query, (f"%{params.CLIENTE}%",))
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


@router.get("/{id}", response_model=List[ClienteResponse])
def obtener_clientes_id(id: int, conn: MySQLConnection = Depends(get_connection)):
    """Obtener cliente por su id (Protegido con JWT)"""
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT CL.idcliente, CL.CLIENTE, PR.nprestamo, PR.vprestamo 
        FROM cliente CL
        JOIN prestamo PR ON CL.idcliente = PR.CODIGO
        WHERE CL.idcliente = %s
    """
    cursor.execute(query, (id,))
    results = cursor.fetchall()
    cursor.close()

    if not results:
        raise HTTPException(
            status_code=404, detail="No se encontraron clientes con prestamos activos."
        )

    now = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    for r in results:
        r["fecha"] = now

    return results
