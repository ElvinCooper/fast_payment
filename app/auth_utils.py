import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
import os
import mysql.connector
from typing import Optional
import uuid

load_dotenv()

# Configuración JWT
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 2

# Esquema de seguridad para Swagger
security = HTTPBearer()


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    jti = str(uuid.uuid4())
    to_encode.update({"exp": expire, "jti": jti})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


REFRESH_TOKEN_EXPIRE_DAYS = 7


def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    jti = str(uuid.uuid4())
    to_encode.update({"exp": expire, "jti": jti, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def is_token_revoked(jti: str) -> bool:
    """Verifica si el token ha sido revocado consultando PostgreSQL"""
    from app.postgres_db import get_pg_connection

    conn = get_pg_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM token_blocklist WHERE jti = %s", (jti,))
        result = cursor.fetchone()
        cursor.close()
        return result is not None
    finally:
        conn.close()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Dependencia para verificar el token JWT en las rutas protegidas"""
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("id")
        user_name: str = payload.get("sub")
        jti: str = payload.get("jti")

        if user_id is None or user_name is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido: faltan datos del usuario",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Verificar si el token está revocado
        if is_token_revoked(jti):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token ha sido revocado",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return {"idusuario": user_id, "username": user_name, "jti": payload.get("jti")}

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="El token ha expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se pudo validar el token",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_user_connection(current_user: dict = Depends(get_current_user)):
    """Dependencia que combina autenticación con conexión dinámica a BD del usuario"""
    from app.database import get_connection as get_db

    user_id = current_user.get("id")
    yield from get_db(user_id=user_id)


def get_db_connection(user: dict = Depends(get_current_user)):
    """Dependencia para obtener conexión dinámica a la base de datos del usuario"""
    from app.database import get_connection as get_main_db

    user_id = user.get("id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado en el token",
        )

    conn = get_main_db.__next__()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM user_db_routing WHERE user_id = %s", (user_id,))
    route = cursor.fetchone()
    cursor.close()
    conn.close()

    if not route:
        raise HTTPException(
            status_code=404,
            detail="No se encontró configuración de base de datos para este usuario",
        )

    try:
        user_db_conn = mysql.connector.connect(
            host=route["ip_address"],
            port=route["port"],
            database=route["db_name"],
            user=route["db_user"],
            password=route["db_password"],
            charset="utf8",
            collation="utf8_general_ci",
        )
        return user_db_conn
    except mysql.connector.Error as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al conectar a la base de datos del usuario: {str(e)}",
        )
