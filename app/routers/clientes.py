from fastapi import APIRouter, HTTPException, Depends
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
            IFNULL(CV.vpendiente, 0)  AS vpendiente,
            IFNULL(MORA.mora_total, 0) AS mora_total
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
        LEFT JOIN (
            SELECT 
                nprestamo,
                SUM(ROUND(mora_calc, 2)) AS mora_total
            FROM (
                SELECT 
                    pa.nprestamo,
                    CASE 
                        WHEN p.fpago IN (1, 4, 5) THEN 
                            (pa.vpendiente * p.mora / 100.0 / 30.0) * DATEDIFF(SYSDATE(), pa.fechaplazo)
                        WHEN p.fpago IN (2, 7) THEN 
                            (pa.vpendiente * p.mora / 100.0 / 4.0 / 7.0) * DATEDIFF(SYSDATE(), pa.fechaplazo)
                        WHEN p.fpago IN (3, 6) THEN 
                            (pa.vpendiente * p.mora / 100.0 / 2.0 / 15.0) * DATEDIFF(SYSDATE(), pa.fechaplazo)
                    END AS mora_calc
                FROM pagos pa
                JOIN prestamo p ON pa.nprestamo = p.nprestamo
                WHERE pa.fechaplazo <= SYSDATE()
                    AND pa.vpendiente > 0
                    AND DATEDIFF(SYSDATE(), pa.fechaplazo) > 0
            ) calc_mora
            GROUP BY nprestamo
        ) MORA ON PR.nprestamo = MORA.nprestamo
            WHERE PR.pagado != 1
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
            SUM(IFNULL(G.vpendiente,0)) AS vpendiente,
            IFNULL(MORA.mora_total, 0) AS mora_total            
            FROM prestamo P        
            JOIN pagos G ON P.nprestamo = G.nprestamo
            LEFT JOIN (
                SELECT 
                    nprestamo,
                    SUM(ROUND(mora_calc, 2)) AS mora_total
                FROM (
                    SELECT 
                        pa.nprestamo,
                        CASE 
                            WHEN p.fpago IN (1, 4, 5) THEN 
                                (pa.vpendiente * p.mora / 100.0 / 30.0) * DATEDIFF(SYSDATE(), pa.fechaplazo)
                            WHEN p.fpago IN (2, 7) THEN 
                                (pa.vpendiente * p.mora / 100.0 / 4.0 / 7.0) * DATEDIFF(SYSDATE(), pa.fechaplazo)
                            WHEN p.fpago IN (3, 6) THEN 
                                (pa.vpendiente * p.mora / 100.0 / 2.0 / 15.0) * DATEDIFF(SYSDATE(), pa.fechaplazo)
                        END AS mora_calc
                    FROM pagos pa
                    JOIN prestamo p ON pa.nprestamo = p.nprestamo
                    WHERE pa.fechaplazo <= SYSDATE()
                        AND pa.vpendiente > 0
                        AND DATEDIFF(SYSDATE(), pa.fechaplazo) > 0
                ) calc_mora
                GROUP BY nprestamo
            ) MORA ON P.nprestamo = MORA.nprestamo
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
        IFNULL(CV.vpendiente, 0) AS vpendiente,
        IFNULL(MORA.mora_total, 0) AS mora_total
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
        LEFT JOIN (
            SELECT 
                nprestamo,
                SUM(ROUND(mora_calc, 2)) AS mora_total
            FROM (
                SELECT 
                    pa.nprestamo,
                    CASE 
                        WHEN p.fpago IN (1, 4, 5) THEN 
                            (pa.vpendiente * p.mora / 100.0 / 30.0) * DATEDIFF(SYSDATE(), pa.fechaplazo)
                        WHEN p.fpago IN (2, 7) THEN 
                            (pa.vpendiente * p.mora / 100.0 / 4.0 / 7.0) * DATEDIFF(SYSDATE(), pa.fechaplazo)
                        WHEN p.fpago IN (3, 6) THEN 
                            (pa.vpendiente * p.mora / 100.0 / 2.0 / 15.0) * DATEDIFF(SYSDATE(), pa.fechaplazo)
                    END AS mora_calc
                FROM pagos pa
                JOIN prestamo p ON pa.nprestamo = p.nprestamo
                WHERE pa.fechaplazo <= SYSDATE()
                    AND pa.vpendiente > 0
                    AND DATEDIFF(SYSDATE(), pa.fechaplazo) > 0
            ) calc_mora
            GROUP BY nprestamo
        ) MORA ON PR.nprestamo = MORA.nprestamo
        WHERE CL.CLIENTE LIKE %s 
        AND CL.CLIENTE IS NOT NULL
        AND PR.pagado != 1
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
               IFNULL(CV.vpendiente, 0) AS vpendiente,
               IFNULL(MORA.mora_total, 0) AS mora_total
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
        LEFT JOIN (
            SELECT 
                nprestamo,
                SUM(ROUND(mora_calc, 2)) AS mora_total
            FROM (
                SELECT 
                    pa.nprestamo,
                    CASE 
                        WHEN p.fpago IN (1, 4, 5) THEN 
                            (pa.vpendiente * p.mora / 100.0 / 30.0) * DATEDIFF(SYSDATE(), pa.fechaplazo)
                        WHEN p.fpago IN (2, 7) THEN 
                            (pa.vpendiente * p.mora / 100.0 / 4.0 / 7.0) * DATEDIFF(SYSDATE(), pa.fechaplazo)
                        WHEN p.fpago IN (3, 6) THEN 
                            (pa.vpendiente * p.mora / 100.0 / 2.0 / 15.0) * DATEDIFF(SYSDATE(), pa.fechaplazo)
                    END AS mora_calc
                FROM pagos pa
                JOIN prestamo p ON pa.nprestamo = p.nprestamo
                WHERE pa.fechaplazo <= SYSDATE()
                    AND pa.vpendiente > 0
                    AND DATEDIFF(SYSDATE(), pa.fechaplazo) > 0
            ) calc_mora
            GROUP BY nprestamo
        ) MORA ON PR.nprestamo = MORA.nprestamo
        WHERE CL.idcliente = %s
        AND PR.pagado != 1
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
