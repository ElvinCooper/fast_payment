from fastapi import APIRouter, HTTPException, Request, Depends
from app.schemas.auth_schema import LoginRequest, LoginResponse, SwitchTenantRequest, SwitchTenantResponse
from app.auth_utils import create_access_token, get_current_user
from app.postgres_db import get_user_db_from_ciausers, get_user_empresas, validate_user_empresa
from app.limiter import limiter


router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])


@router.post("/login", response_model=LoginResponse)
@limiter.limit("10/minute")
def login(
    request: Request,
    login_data: LoginRequest,
):
    """Verificar credenciales de usuario y generar token JWT"""

    user_db_info = get_user_db_from_ciausers(login_data.usuario, login_data.password)

    if not user_db_info:
        raise HTTPException(status_code=401, detail="Usuario o clave incorrectos")

    if user_db_info.get("estatus") != 1:
        raise HTTPException(
            status_code=403, detail="Usuario inactivo. Contacte al administrador"
        )

    user_id = user_db_info["idusers"]
    db_asignada = user_db_info["db_asignada"]
    empresa_id = user_db_info["empresa_id"]

    # Obtener empresas del usuario
    empresas = get_user_empresas(user_id)

    # Determinar si necesita selección
    requires_selection = len(empresas) > 1

    # Generar JWT con db_name
    access_token = create_access_token(
        data={
            "sub": login_data.usuario,
            "id": user_id,
            "db_name": db_asignada,
            "empresa_id": empresa_id,
            "tipouser": user_db_info.get("tipouser"),
            "empresa": user_db_info.get("empresa"),
            "idcia": user_db_info.get("idcia"),
        }
    )

    return {
        "idusuario": user_id,
        "usuario": login_data.usuario,
        "access_token": access_token,
        "token_type": "bearer",
        "message": "Login exitoso",
        "user_db": db_asignada,
        "db_name": db_asignada,
        "empresa": user_db_info.get("empresa"),
        "tipouser": user_db_info.get("tipouser"),
        "empresas": empresas if requires_selection else None,
        "requires_selection": requires_selection,
    }


@router.post("/switch-tenant", response_model=SwitchTenantResponse)
@limiter.limit("20/minute")
def switch_tenant(
    request: Request,
    tenant_data: SwitchTenantRequest,
    current_user: dict = Depends(get_current_user),
):
    """Cambiar de empresa/tenant - genera nuevo JWT con db_name"""

    user_id = current_user.get("idusuario")
    empresa_id = tenant_data.empresa_id

    # Validar que el usuario pertenece a la empresa
    empresa_info = validate_user_empresa(user_id, empresa_id)

    if not empresa_info:
        raise HTTPException(
            status_code=403,
            detail="No tienes acceso a esta empresa"
        )

    # Generar nuevo JWT con la nueva BD
    new_token = create_access_token(
        data={
            "sub": current_user.get("username"),
            "id": user_id,
            "db_name": empresa_info["descbd"],
            "empresa_id": empresa_id,
            "tipouser": current_user.get("tipouser"),
            "empresa": empresa_info["cidescripcion"],
            "idcia": empresa_info["idcia"],
        }
    )

    return {
        "access_token": new_token,
        "token_type": "bearer",
        "db_name": empresa_info["descbd"],
        "empresa": empresa_info["cidescripcion"],
        "message": "Tenant cambiado exitosamente"
    }
