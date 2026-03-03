from fastapi import APIRouter, HTTPException, Depends
from app.schemas.auth_schema import LoginRequest, LoginResponse
from app.database import get_connection
from app.auth_utils import create_access_token
from mysql.connector import MySQLConnection


router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])


@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest, conn: MySQLConnection = Depends(get_connection)):
    """Verificar credenciales de usuario y generar token JWT"""
    cursor = conn.cursor(dictionary=True)

    # Consulta por usuario y clave (varchar 45)
    query = "SELECT idusuario, usuario FROM usuario WHERE usuario = %s AND clave = %s"
    cursor.execute(query, (request.usuario, request.password))
    user = cursor.fetchone()
    cursor.close()

    if not user:
        raise HTTPException(
            status_code=401, detail="Usuario o clave incorrectos"
        )

    # Crear el token de acceso
    access_token = create_access_token(
        data={"sub": user["usuario"], "id": user["idusuario"]}
    )

    return {
        "idusuario": user["idusuario"],
        "usuario": user["usuario"],
        "access_token": access_token,
        "token_type": "bearer",
        "message": "Login exitoso"
    }
