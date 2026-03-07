from fastapi import APIRouter, HTTPException, Depends
from app.schemas.routing_schema import UserDBRoutingResponse, UserDBRoutingCreate
from app.database import get_connection
from app.auth_utils import get_current_user
from mysql.connector import MySQLConnection
from typing import List
import mysql.connector

router = APIRouter(
    prefix="/api/v1/admin",
    tags=["Admin"],
)


@router.get("/routing", response_model=List[UserDBRoutingResponse])
def get_all_routes(
    conn: MySQLConnection = Depends(get_connection),
    current_user: dict = Depends(get_current_user),
):
    """Obtener todas las rutas de base de datos"""
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM user_db_routing ORDER BY id DESC")
    results = cursor.fetchall()
    cursor.close()
    return results


@router.post("/routing", response_model=UserDBRoutingResponse)
def create_route(
    route: UserDBRoutingCreate,
    conn: MySQLConnection = Depends(get_connection),
    current_user: dict = Depends(get_current_user),
):
    """Crear una nueva ruta de base de datos"""
    cursor = conn.cursor()
    query = """
        INSERT INTO user_db_routing (user_id, ip_address, port, db_name, db_user, db_password)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    cursor.execute(
        query,
        (
            route.user_id,
            route.ip_address,
            route.port,
            route.db_name,
            route.db_user,
            route.db_password,
        ),
    )
    conn.commit()
    route_id = cursor.lastrowid
    cursor.close()

    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM user_db_routing WHERE id = %s", (route_id,))
    result = cursor.fetchone()
    cursor.close()
    return result


@router.get("/server/{server_id}/databases")
def get_server_databases(
    server_id: int,
    conn: MySQLConnection = Depends(get_connection),
    current_user: dict = Depends(get_current_user),
):
    """Obtener las bases de datos disponibles en un servidor"""
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM user_db_routing WHERE id = %s", (server_id,))
    route = cursor.fetchone()
    cursor.close()

    if not route:
        raise HTTPException(status_code=404, detail="Servidor no encontrado")

    try:
        temp_conn = mysql.connector.connect(
            host=route["ip_address"],
            port=route["port"],
            user=route["db_user"],
            password=route["db_password"],
            connect_timeout=5,
        )
        temp_cursor = temp_conn.cursor()
        temp_cursor.execute("SHOW DATABASES")
        databases = [
            db[0]
            for db in temp_cursor.fetchall()
            if db[0] not in ("information_schema", "performance_schema", "mysql", "sys")
        ]
        temp_cursor.close()
        temp_conn.close()
        return {"databases": databases}
    except mysql.connector.Error as e:
        raise HTTPException(
            status_code=500, detail=f"Error al conectar al servidor: {str(e)}"
        )
