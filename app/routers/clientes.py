from fastapi import APIRouter, HTTPException, Depends, Query
from app.schemas.cliente_schema import (
    ClienteResponse,
    ParamNombre,
    CuotaVencidaResponse,
)
from typing import List
from app.auth_utils import get_user_connection
from mysql.connector import MySQLConnection
from datetime import datetime

router = APIRouter(
    prefix="/api/v1/clientes",
    tags=["Clientes"],
)


@router.get("/", response_model=List[ClienteResponse])
def obtener_clientes(conn: MySQLConnection = Depends(get_user_connection)):
    """Obtener todos los clientes con prestamos activos"""
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT
            CL.idcliente,
            CL.CLIENTE,
            PR.nprestamo,
            PR.vprestamo,
            PR.FECHAP,
            PR.fechav,
            PR.cel,
            CASE
                WHEN PR.pagado = 0 THEN 'con cuota vencida' ELSE 'sin cuota vencida' END AS estado_cuota,
            IFNULL(CV.cantidad_cutas, 0)     AS cantidad_cutas,
            IFNULL(CV.vpendiente, 0)  AS vpendiente
        FROM cliente CL
        JOIN prestamo PR ON CL.idcliente = PR.codigo
        LEFT JOIN (
            SELECT
                G.nprestamo,
                COUNT(G.ncuotas) as cantidad_cutas,
                SUM(IFNULL(G.vpendiente, 0)) AS vpendiente
            FROM pagos G
            WHERE G.fechaven <= SYSDATE()
            AND G.estatus = 0
            GROUP BY G.nprestamo) CV ON PR.nprestamo = CV.nprestamo
        ORDER BY pr.CLIENTE   
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
        if r.get("FECHAP"):
            r["FECHAP"] = r["FECHAP"].strftime("%d-%m-%Y")
        if r.get("fechav"):
            r["fechav"] = r["fechav"].strftime("%d-%m-%Y")

    return results


@router.get("/cuotas/vencidas", response_model=List[CuotaVencidaResponse])
def listado_cuotas_vencidas(conn: MySQLConnection = Depends(get_user_connection)):
    """Listar los clientes con cuotas vencidas en el sistema"""
    cursor = conn.cursor(dictionary=True)

    query = """
            SELECT  P.NPRESTAMO,
            P.CODIGO,
            P.CLIENTE ,
            P.FECHAP ,
            P.fechav ,        
            P.cel,        
            COUNT(G.ncuotas) AS ncuotas,
            SUM(IFNULL(G.vpendiente,0)) AS vpendiente            
            FROM prestamo P        
            JOIN pagos G ON P.nprestamo = G.nprestamo
            WHERE G.fechaven <= SYSDATE() 
            AND G.estatus = 0
            AND P.pagado = 0
            GROUP BY G.nprestamo
            ORDER BY P.cliente
        """

    cursor.execute(
        query,
    )
    resultado = cursor.fetchall()
    cursor.close()

    if not resultado:
        raise HTTPException(
            status_code=404, detail="No se encontraron clientes con cuotas vencidas"
        )

    return resultado


@router.get(
    "/buscar",
    response_model=List[ClienteResponse],
)
def buscar_clientes_por_nombre(
    params: ParamNombre = Depends(),
    conn: MySQLConnection = Depends(get_user_connection),
):
    """Buscar clientes por nombre)"""
    cursor = conn.cursor(dictionary=True)

    query = """
       SELECT
       CL.idcliente,
       CL.CLIENTE,
       PR.nprestamo,
       PR.vprestamo,
       PR.FECHAP,
       PR.fechav,
       PR.cel,
       CASE
           WHEN PR.pagado = 0 THEN 'con cuota vencida'
           ELSE 'sin cuota vencida'
       END AS estado_cuota,
       IFNULL(CV.cantidad_cutas, 0) AS cantidad_cutas,
       IFNULL(CV.vpendiente, 0) AS vpendiente
       FROM cliente CL
       JOIN prestamo PR ON CL.idcliente = PR.CODIGO
       LEFT JOIN (
           SELECT
               G.nprestamo,
               COUNT(G.ncuotas) as cantidad_cutas,
               SUM(IFNULL(G.vpendiente, 0)) AS vpendiente
           FROM pagos G
           WHERE G.fechaven <= SYSDATE()
           AND G.estatus = 0
           GROUP BY G.nprestamo
       ) CV ON PR.nprestamo = CV.nprestamo
       WHERE CL.CLIENTE LIKE %s AND CL.CLIENTE IS NOT NULL
       LIMIT 20;
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
        if r.get("FECHAP"):
            r["FECHAP"] = r["FECHAP"].strftime("%d-%m-%Y")
        if r.get("fechav"):
            r["fechav"] = r["fechav"].strftime("%d-%m-%Y")

    return resultados


@router.get("/{id}", response_model=List[ClienteResponse])
def obtener_clientes_id(id: int, conn: MySQLConnection = Depends(get_user_connection)):
    """Obtener cliente por su id"""
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT CL.idcliente, 
               CL.CLIENTE,
               PR.nprestamo,
               PR.vprestamo,
               PR.FECHAP,
               PR.fechav,
               PR.cel,
               CASE 
                WHEN PR.pagado = 0 THEN 'con cuota vencida' ELSE 'sin cuota vencida'
               END AS estado_cuota,
               IFNULL(CV.cantidad_cutas, 0) AS cantidad_cutas,
               IFNULL(CV.vpendiente, 0) AS vpendiente
        FROM cliente CL
        JOIN prestamo PR ON CL.idcliente = PR.CODIGO
        LEFT JOIN (
            SELECT
                G.nprestamo,
                COUNT(G.ncuotas) as cantidad_cutas,
                SUM(IFNULL(G.vpendiente, 0)) AS vpendiente
            FROM pagos G
            WHERE G.fechaven <= SYSDATE()
            AND G.estatus = 0
            GROUP BY G.nprestamo
        ) CV ON PR.nprestamo = CV.nprestamo
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
        if r.get("FECHAP"):
            r["FECHAP"] = r["FECHAP"].strftime("%d-%m-%Y")
        if r.get("fechav"):
            r["fechav"] = r["fechav"].strftime("%d-%m-%Y")

    return results
