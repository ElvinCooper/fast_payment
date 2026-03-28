from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from app.routers import clientes, pagos, usuarios, auth, admin
from app.middleware.security_headers import SecurityHeadersMiddleware
from datetime import datetime
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.limiter import limiter
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

# Configurar Limiter (por IP del cliente)
# Límite global por defecto: 100 peticiones por minuto

app = FastAPI(
    title="Sistema de Pagos BioCamila",
    description="Backend para gestión de cobros y pagos de clientes (Protegido con JWT y Rate Limit)",
    version="1.0.0",
)

# Registrar el Limiter y su manejador de errores
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Manejar errores de validación y hacer logging"""
    errors = exc.errors()
    logger.error(f"Validation error on {request.method} {request.url.path}: {errors}")
    from fastapi.responses import JSONResponse
    from fastapi.encoders import jsonable_encoder

    return JSONResponse(
        status_code=422,
        content={"detail": jsonable_encoder(errors)},
    )


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(SecurityHeadersMiddleware)

app.include_router(clientes.router)
app.include_router(pagos.router)
app.include_router(usuarios.router)
app.include_router(auth.router)
app.include_router(admin.router)


@app.get("/")
@limiter.limit("5/minute")  # Límite más estricto para el root
def root(request: Request):
    return {"message": "API activa", "timestamp": datetime.now()}
