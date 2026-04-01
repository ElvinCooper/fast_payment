from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from app.schemas.usuario_schema import UserBase
from app.auth_utils import (
    get_current_user,
    create_access_token,
    create_refresh_token,
    is_token_revoked,
)

router = APIRouter(
    prefix="/api/v1/usuarios",
    tags=["Usuarios"],
)


def _agregar_token_blocklist(jti: str, idusuario: int):
    """Inserta el token en la blocklist de PostgreSQL"""
    from app.postgres_db import get_pg_connection

    conn = get_pg_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO token_blocklist (jti, fecha_creacion, idusuario) VALUES (%s, CURRENT_DATE, %s)",
            (jti, idusuario),
        )
        conn.commit()
        cursor.close()
    finally:
        conn.close()


@router.get("/me", response_model=UserBase)
def obtener_usuario_actual(current_user: dict = Depends(get_current_user)):
    """Obtener el usuario autenticado actual"""
    return {
        "idusuario": current_user["idusuario"],
        "usuario": current_user["username"],
        "db_asignada": current_user["db_name"],  
        "empresa": current_user.get("empresa", ""),
        "tipouser": current_user.get("tipouser", ""),
        "empresas": current_user.get("empresas"),
        "requires_selection": current_user.get("requires_selection")
    }


@router.post("/logout")
def logout(
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
):
    """Invalidar el token actual agregándolo a la blocklist"""
    background_tasks.add_task(
        _agregar_token_blocklist,
        current_user["jti"],
        current_user["idusuario"],
    )

    return {"message": "Sesión cerrada con éxito"}


@router.post("/refresh")
def refresh_token(
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
):
    """Renovar los tokens de acceso manteniendo la información del tenant"""
    from app.schemas.auth_schema import TokenRefreshResponse

    jti = current_user["jti"]

    if is_token_revoked(jti):
        raise HTTPException(status_code=401, detail="Token ha sido revocado")

    background_tasks.add_task(
        _agregar_token_blocklist,
        jti,
        current_user["idusuario"],
    )

    # Mantener toda la información del usuario incluyendo tenant
    identity = {
        "sub": current_user["username"],
        "id": current_user["idusuario"],
        "db_name": current_user["db_name"],  # Mantener tenant activo
        "empresa_id": current_user["empresa_id"],
        "tipouser": current_user.get("tipouser"),
        "empresa": current_user.get("empresa"),
        "idcia": current_user.get("idcia"),
    }
    new_access_token = create_access_token(data=identity)
    new_refresh_token = create_refresh_token(data=identity)

    return TokenRefreshResponse(
        access_token=new_access_token, refresh_token=new_refresh_token
    )
