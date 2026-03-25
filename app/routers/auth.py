from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Request
from app.schemas.auth_schema import LoginRequest, LoginResponse
from app.database import get_connection
from app.auth_utils import create_access_token
from app.postgres_db import get_user_database, get_user_type
from app.limiter import limiter
from mysql.connector import MySQLConnection


router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])


@router.post("/login", response_model=LoginResponse)
@limiter.limit("10/minute")
def login(
    request: Request,
    login_data: LoginRequest,
    # api_key: str = Depends(get_api_key),
    conn: MySQLConnection = Depends(get_connection),
):
    """Verificar credenciales de usuario y generar token JWT"""
    cursor = conn.cursor(dictionary=True)

    query = "SELECT idusuario, usuario FROM usuario WHERE usuario = %s AND clave = %s"
    cursor.execute(query, (login_data.usuario, login_data.password))
    user = cursor.fetchone()
    cursor.close()

    if not user:
        raise HTTPException(status_code=401, detail="Usuario o clave incorrectos")

    user_db = get_user_database(user["idusuario"])
    db_asignada = user_db or "default"
    user_type = get_user_type(user["idusuario"])

    access_token = create_access_token(
        data={
            "sub": user["usuario"],
            "id": user["idusuario"],
            "db_asignada": db_asignada,
        }
    )

    return {
        "idusuario": user["idusuario"],
        "usuario": user["usuario"],
        "access_token": access_token,
        "token_type": "bearer",
        "message": "Login exitoso",
        "user_db": db_asignada,
        "tipouser": user_type,
    }
