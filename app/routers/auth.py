from fastapi import APIRouter, HTTPException, Depends, Request
from app.schemas.auth_schema import LoginRequest, LoginResponse
from app.database import get_connection
from app.auth_utils import create_access_token, get_user_connection
from app.postgres_db import get_user_type, get_user_db_from_ciausers
from app.limiter import limiter
from mysql.connector import MySQLConnection


router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])


@router.post("/login", response_model=LoginResponse)
@limiter.limit("10/minute")
def login(
    request: Request,
    login_data: LoginRequest,
):
    """Verificar credenciales de usuario y generar token JWT"""

    # Primero buscar en ciausers para obtener la BD correcta
    user_db_info = get_user_db_from_ciausers(login_data.usuario, login_data.password)

    if not user_db_info:
        raise HTTPException(status_code=401, detail="Usuario o clave incorrectos")

    if user_db_info.get("estatus") != 1:
        raise HTTPException(
            status_code=403, detail="Usuario inactivo. Contacte al administrador"
        )

    db_asignada = user_db_info["db_asignada"]
    user_id_cia = user_db_info["idusers"]

    # Conectar a la BD del usuario
    from app.database import HOST, PORT, USER, DBPASSWORD
    import mysql.connector

    user_conn = mysql.connector.connect(
        host=HOST,
        port=PORT,
        user=USER,
        password=DBPASSWORD,
        database=db_asignada,
        charset="utf8",
    )
    cursor = user_conn.cursor(dictionary=True)

    query = "SELECT idusuario, usuario FROM usuario WHERE usuario = %s"
    cursor.execute(query, (login_data.usuario,))
    user = cursor.fetchone()
    cursor.close()
    user_conn.close()

    if not user:
        raise HTTPException(status_code=401, detail="Usuario o clave incorrectos")

    user_type = get_user_type(user_id_cia)
    empresa = user_db_info.get("empresa", "")

    access_token = create_access_token(
        data={
            "sub": user["usuario"],
            "id": user_id_cia,
            "db_asignada": db_asignada,
        }
    )

    return {
        "idusuario": user["idusuario"],
        "usuario": user["usuario"],
        "access_token": access_token,
        "token_type": "bearer",  # nosec: B105
        "message": "Login exitoso",
        "user_db": db_asignada,
        "empresa": empresa,
        "tipouser": user_type,
    }
