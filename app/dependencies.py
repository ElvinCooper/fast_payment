from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from app.config import get_settings
from app.mysql_db import get_user_empresas

settings = get_settings()
security = HTTPBearer()


def create_access_token(data: dict) -> str:
    from datetime import datetime, timedelta, timezone
    import uuid

    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(hours=settings.EXPIRE_HOURS)
    jti = str(uuid.uuid4())
    to_encode.update({"exp": expire, "jti": jti})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    from datetime import datetime, timedelta, timezone
    import uuid

    REFRESH_TOKEN_EXPIRE_DAYS = 7
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    jti = str(uuid.uuid4())
    to_encode.update({"exp": expire, "jti": jti, "type": "refresh"})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def is_token_revoked(jti: str) -> bool:
    from app.mysql_db import get_pg_connection

    conn = get_pg_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM token_blocklist WHERE jti = %s", (jti,))
        result = cursor.fetchone()
        cursor.close()
        return result is not None
    finally:
        conn.close()


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
) -> dict:
    """Dependencia para verificar el token JWT en las rutas protegidas"""
    token = credentials.credentials
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id = payload.get("id")
        user_name = payload.get("sub")
        jti = payload.get("jti")
        db_name = payload.get("db_name")

        if user_id is None or user_name is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido: faltan datos del usuario",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not db_name:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Tenant no seleccionado",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if is_token_revoked(jti):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token ha sido revocado",
                headers={"WWW-Authenticate": "Bearer"},
            )

        empresas = get_user_empresas(user_id)
        requires_selection = len(empresas) > 1

        return {
            "idusuario": user_id,
            "username": user_name,
            "jti": payload.get("jti"),
            "db_name": db_name,
            "empresa_id": payload.get("empresa_id"),
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


CurrentUserDep = Annotated[dict, Depends(get_current_user)]


def get_user_connection(current_user: CurrentUserDep):
    """Dependencia que combina autenticación con conexión dinámica a BD del usuario"""
    from app.database import get_connection as get_db

    user_id = current_user.get("idusuario")
    db_name = current_user.get("db_name")
    yield from get_db(user_id=user_id, db_name=db_name)


def get_db_from_token(current_user: CurrentUserDep) -> str | None:
    """Extrae db_name del token para usarlo en la conexión"""
    return current_user.get("db_name")
