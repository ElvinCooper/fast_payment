from fastapi import APIRouter, HTTPException, Depends, Body
from app.schemas.routing_schema import UserCIAUpdate
from app.auth_utils import get_current_user, get_user_connection
from app.database import get_cia_connection, HOST, PORT, USER, DBPASSWORD
from mysql.connector import MySQLConnection
import mysql.connector

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
    conn: MySQLConnection = Depends(get_cia_connection),
):
    """Lista usuarios de la compañía del usuario logueado"""

    cursor = conn.cursor(dictionary=True)
    query = """
            SELECT idusers, usuario, tipouser FROM ciausers
            WHERE idcia = %s
            ORDER BY idusers            
            """
    cursor.execute(query, (current_user["idcia"],))
    results = cursor.fetchall()
    cursor.close()

    return [
        {
            "idusuario": user["idusers"],
            "usuario": user["usuario"],
            "tipouser": user["tipouser"],
        }
        for user in results
    ]


@router.put("/user/cia")
def actualizar_usuario_cia(
    user_data: UserCIAUpdate = Body(...),
    current_user: dict = Depends(get_current_user),
):
    """Actualiza datos de usuario en la tabla ciausers (clave, estatus, tipouser)"""
    user_id = current_user.get("idusuario")
    if not is_admin(user_id):
        raise HTTPException(
            status_code=403,
            detail="Acceso denegado. Solo administradores pueden acceder a esta función",
        )

    from app.postgres_db import actualizar_usuario_cia as actualizar_cia

    # Solo pasar campos que fueron enviados explícitamente en el request
    campos_enviados = user_data.model_fields_set
    idcia = current_user.get("idcia")
    result = actualizar_cia(
        user_data.idusers,
        idcia,
        clave=user_data.clave if "clave" in campos_enviados else None,
        estatus=user_data.estatus if "estatus" in campos_enviados else None,
        tipouser=user_data.tipouser if "tipouser" in campos_enviados else None,
    )

    if "no encontrado" in result.lower():
        raise HTTPException(status_code=404, detail=result)

    return {"message": result}


@router.get("/user/tipos")
def listar_tipos_usuario(current_user: dict = Depends(get_current_user)):
    """Lista los tipos de usuario disponibles en ciausers"""
    user_id = current_user.get("idusuario")
    if not is_admin(user_id):
        raise HTTPException(
            status_code=403,
            detail="Acceso denegado. Solo administradores pueden acceder a esta función",
        )

    from app.postgres_db import get_tipos_usuario

    tipos = get_tipos_usuario()
    return {"tipos_usuario": tipos}


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
