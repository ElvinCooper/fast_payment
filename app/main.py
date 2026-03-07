from fastapi import FastAPI, Request
from app.routers import clientes, pagos, usuarios, auth, admin
from datetime import datetime
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Configurar Limiter (por IP del cliente)
# Límite global por defecto: 100 peticiones por minuto
limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])

app = FastAPI(
    title="Sistema de Cobros",
    description="Backend para gestión de cobros y pagos de clientes (Protegido con JWT y Rate Limit)",
    version="1.0.0",
)

# Registrar el Limiter y su manejador de errores
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.include_router(clientes.router)
app.include_router(pagos.router)
app.include_router(usuarios.router)
app.include_router(auth.router)
app.include_router(admin.router)


@app.get("/")
@limiter.limit("5/minute")  # Límite más estricto para el root
def root(request: Request):
    return {"message": "API activa", "timestamp": datetime.now()}
