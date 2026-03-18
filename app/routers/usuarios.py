from fastapi import APIRouter, HTTPException, Depends
from app.schemas.usuario_schema import UserBase
from app.auth_utils import (
    get_user_connection,
    get_current_user,
    create_access_token,
    create_refresh_token,
    is_token_revoked,
)
from mysql.connector import MySQLConnection
from typing import List

router = APIRouter(
    prefix="/api/v1/usuarios",
    tags=["Usuarios"],
)


@router.get("/", response_model=List[UserBase])
def obtener_usuarios(conn: MySQLConnection = Depends(get_user_connection)):
    """Obtener todos los usuarios del sistema"""
    cursor = conn.cursor(dictionary=True)

    query = "SELECT idusuario, usuario FROM usuario"
    cursor.execute(
        query,
    )
    usuarios = cursor.fetchall()
    cursor.close()

    if not usuarios:
        raise HTTPException(status_code=404, detail="No existen usuarios en el sistema")

    return usuarios


@router.get("/me", response_model=UserBase)
def obtener_usuario_actual(current_user: dict = Depends(get_current_user)):
    """Obtener el usuario autenticado actual"""
    return {"idusuario": current_user["idusuario"], "usuario": current_user["username"]}


@router.post("/logout")
def logout(current_user: dict = Depends(get_current_user)):
    """Invalidar el token actual agregándolo a la blocklist"""
    from app.postgres_db import get_pg_connection

    conn = get_pg_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO token_blocklist (jti, fecha_creacion, idusuario) VALUES (%s, CURRENT_DATE, %s)",
            (
                current_user["jti"],
                current_user["idusuario"],
            ),
        )
        conn.commit()
        cursor.close()
    finally:
        conn.close()

    return {"message": "Sesión cerrada con éxito"}


@router.post("/refresh")
def refresh_token(current_user: dict = Depends(get_current_user)):
    """Renovar los tokens de acceso"""
    from app.postgres_db import get_pg_connection
    from app.schemas.auth_schema import TokenRefreshResponse

    jti = current_user["jti"]

    if is_token_revoked(jti):
        raise HTTPException(status_code=401, detail="Token ha sido revocado")

    conn = get_pg_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO token_blocklist (jti, fecha_creacion, idusuario) VALUES (%s, CURRENT_DATE, %s)",
            (jti, current_user["idusuario"]),
        )
        conn.commit()
        cursor.close()
    finally:
        conn.close()

    identity = {"sub": current_user["username"], "id": current_user["idusuario"]}
    new_access_token = create_access_token(data=identity)
    new_refresh_token = create_refresh_token(data=identity)

    return TokenRefreshResponse(
        access_token=new_access_token, refresh_token=new_refresh_token
    )


@router.get("/{id}", response_model=UserBase)
def obtener_usuario_id(id: int, conn: MySQLConnection = Depends(get_user_connection)):
    """Obtener un usuario por su id"""
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
