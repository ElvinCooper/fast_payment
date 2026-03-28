from fastapi import APIRouter, HTTPException, Request
from app.schemas.auth_schema import LoginRequest, LoginResponse
from app.auth_utils import create_access_token
from app.postgres_db import get_user_db_from_ciausers
from app.limiter import limiter


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
    user_type = user_db_info.get("tipouser")
    empresa = user_db_info.get("empresa", "")
    idcia = user_db_info.get("idcia")

    access_token = create_access_token(
        data={
            "sub": login_data.usuario,
            "id": user_id_cia,
            "db_asignada": db_asignada,
            "tipouser": user_type,
            "empresa": empresa,
            "idcia": idcia,
        }
    )

    return {
        "idusuario": user_id_cia,
        "usuario": login_data.usuario,
        "access_token": access_token,
        "token_type": "bearer",  # nosec: B105
        "message": "Login exitoso",
        "user_db": db_asignada,
        "empresa": empresa,
        "tipouser": user_type,
    }
