from fastapi import APIRouter, HTTPException, Depends, Body
from app.schemas.routing_schema import UserDBRoutingUpdate
from app.auth_utils import get_current_user, get_user_connection
from mysql.connector import MySQLConnection
import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()
HOST = os.getenv("HOST")
PORT = os.getenv("PORT")
USER = os.getenv("USER")
DBPASSWORD = os.getenv("DBPASSWORD")

router = APIRouter(
    prefix="/api/v1/admin",
    tags=["Admin"],
)


def is_admin(user_id: int | None) -> bool:
    """Verifica si el usuario es administrador basándose en ciausers.tipouser"""
    if user_id is None:
        return False
    from app.postgres_db import get_user_type

    user_type = get_user_type(user_id)
    return user_type is not None and user_type != "standard"


@router.get("/users")
def system_users(
    current_user: dict = Depends(get_current_user),
    conn: MySQLConnection = Depends(get_user_connection),
):
    """Lista usuarios con acceso al sistema"""

    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT idusuario, usuario FROM usuario ORDER BY idusuario")
    results = cursor.fetchall()
    cursor.close()

    return [
        {"idusuario": user["idusuario"], "usuario": user["usuario"]} for user in results
    ]


@router.put("/user/routing")
def asignar_acceso(
    user_data: UserDBRoutingUpdate = Body(...),
    current_user: dict = Depends(get_current_user),
    conn: MySQLConnection = Depends(get_user_connection),
):
    # Validar que el usuario sea administrador
    user_id = current_user.get("idusuario")
    if not is_admin(user_id):
        raise HTTPException(
            status_code=403,
            detail="Acceso denegado. Solo administradores pueden acceder a esta función",
        )

    # Validar que se envió al menos la clave
    if user_data.clave is None:
        raise HTTPException(status_code=400, detail="Debe enviar la 'clave'")

    from app.postgres_db import asignar_db_usuario

    result = asignar_db_usuario(user_data.idusuario, user_data.clave)

    if "no encontrado" in result.lower():
        raise HTTPException(status_code=404, detail=result)

    return {"message": "Usuario actualizado exitosamente"}


@router.get("/server/databases")
def get_server_databases(
    conn: MySQLConnection = Depends(get_user_connection),
    current_user: dict = Depends(get_current_user),
):
    """Obtener las bases de datos disponibles en el servidor"""

    user_id = current_user.get("idusuario")
    if not is_admin(user_id):
        raise HTTPException(
            status_code=403,
            detail="Acceso denegado. Solo administradores pueden acceder a esta función",
        )

    try:
        temp_conn = mysql.connector.connect(
            host=HOST,
            port=PORT,
            user=USER,
            password=DBPASSWORD,
            charset="utf8",
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


@router.get("/empresas")
def get_empresas(
    current_user: dict = Depends(get_current_user),
):
    """Obtiene todas las empresas registradas"""
    user_id = current_user.get("idusuario")
    if not is_admin(user_id):
        raise HTTPException(
            status_code=403,
            detail="Acceso denegado. Solo administradores pueden acceder a esta función",
        )

    from app.postgres_db import get_all_empresas

    empresas = get_all_empresas()
    return {"empresas": empresas}
