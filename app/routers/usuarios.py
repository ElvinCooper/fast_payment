from fastapi import APIRouter, HTTPException, Depends
from app.schemas.usuario_schema import UserBase
from app.database import get_connection
from app.auth_utils import get_current_user
from mysql.connector import MySQLConnection
from typing import List

router = APIRouter(
    prefix="/api/v1/usuarios", 
    tags=["Usuarios"],
    dependencies=[Depends(get_current_user)]
)


@router.get("/", response_model=List[UserBase])
def obtener_usuarios(conn: MySQLConnection = Depends(get_connection)):
    """Obtener todos los usuarios del sistema"""
    cursor = conn.cursor(dictionary=True)

    query = "SELECT idusuario, usuario FROM usuario"
    cursor.execute(query,)
    usuarios = cursor.fetchall()
    cursor.close()

    if not usuarios:
        raise HTTPException(
            status_code=404, detail="No existen usuarios en el sistema"
        )

    return usuarios



@router.get("/{id}", response_model=UserBase)
def obtener_usuario_id(id: int, conn: MySQLConnection = Depends(get_connection)):
    """Obtener un usuario por su id """
    cursor = conn.cursor(dictionary=True)

    query = "SELECT idusuario, usuario FROM usuario WHERE idusuario = %s"
    cursor.execute(query, (id,))
    usuario = cursor.fetchone()
    cursor.close()

    if not usuario:
        raise HTTPException(
            status_code=404, detail="No se encontro ningun usuario con este id"
        )

    return usuario
