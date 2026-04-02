import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
import os
import uuid
from app.postgres_db import get_user_empresas

load_dotenv()

# Configuración JWT
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = os.getenv("EXPIRE_HOURS", "2")

# Esquema de seguridad para Swagger
security = HTTPBearer()


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        hours=int(ACCESS_TOKEN_EXPIRE_HOURS)
    )
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
        db_name = payload.get("db_name")

        if user_id is None or user_name is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido: faltan datos del usuario",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Validar que existe db_name (tenant activo)
        if not db_name:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Tenant no seleccionado",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Verificar si el token está revocado
        if is_token_revoked(jti):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token ha sido revocado",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Obtener empresas del usuario
        empresas = get_user_empresas(user_id)

        # Determinar si necesita selección
        requires_selection = len(empresas) > 1

        return {
            "idusuario": user_id,
            "username": user_name,
            "jti": payload.get("jti"),
            "db_name": db_name,  # NUEVO
            "empresa_id": payload.get("empresa_id"),  # NUEVO
            "tipouser": payload.get("tipouser"),
            "empresa": payload.get("empresa"),
            "idcia": payload.get("idcia"),
            "empresas": empresas if requires_selection else None,
            "requires_selection": requires_selection,
        }

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

    user_id = current_user.get("idusuario")
    db_name = current_user.get("db_name")
    yield from get_db(user_id=user_id, db_name=db_name)


def get_db_from_token(current_user: dict = Depends(get_current_user)):
    """Extrae db_name del token para usarlo en la conexión"""
    return current_user.get("db_name")
