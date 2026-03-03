from fastapi import FastAPI
from app.routers import clientes, pagos, usuarios, auth
from datetime import datetime

app = FastAPI(
    title="Sistema de Cobros",
    description="Backend para gestión de cobros y pagos de clientes",
    version="1.0.0",
)

app.include_router(clientes.router)
app.include_router(pagos.router)
app.include_router(usuarios.router)
app.include_router(auth.router)


@app.get("/")
def root():
    return {"message": "API activa", "timestamp": datetime.now()}
