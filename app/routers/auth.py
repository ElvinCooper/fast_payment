from fastapi import APIRouter, HTTPException, Depends
from app.schemas.auth_schema import LoginRequest, LoginResponse
from app.database import get_connection
from mysql.connector import MySQLConnection


router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])


@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest, conn: MySQLConnection = Depends(get_connection)):
    """Verificar credenciales de usuario"""
    cursor = conn.cursor(dictionary=True)

    # Nota: estamos buscando por usuario y clave directamente de la tabla usuario.
    query = "SELECT idusuario, usuario FROM usuario WHERE usuario = %s AND clave = %s"
    cursor.execute(query, (request.usuario, request.password))
    user = cursor.fetchone()
    cursor.close()

    if not user:
        raise HTTPException(
            status_code=401, detail="Usuario o clave incorrectos"
        )

    return {
        "idusuario": user["idusuario"],
        "usuario": user["usuario"],
        "message": "Login exitoso"
    }
