# 🚀 Fast Payment - Sistema de Cobros API

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python)](https://www.python.org/)
[![MySQL](https://img.shields.io/badge/MySQL-8.0-blue?style=for-the-badge&logo=mysql)](https://www.mysql.com/)
[![JWT](https://img.shields.io/badge/JWT-Auth-red?style=for-the-badge&logo=jwt)](https://jwt.io/)

Una API REST robusta y moderna para la gestión de cobros y pagos de clientes, construida con FastAPI y diseñada para operar en entornos de producción serverless.

## 📋 Tabla de Contenido

- [Características](#-características)
- [Arquitectura](#-arquitectura)
- [Requisitos](#-requisitos)
- [Instalación](#-instalación)
- [Configuración](#-configuración)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Endpoints API](#-endpoints-api)
- [Sistema de Multi-Tenancy](#-sistema-de-multi-tenancy)
- [Ejemplos de Uso](#-ejemplos-de-uso)
- [Testing](#-testing)
- [Deployment](#-deployment)
- [Contacto](#-contacto)

## ✨ Características

- 🔐 **Autenticación JWT**: Tokens seguros con expiración configurable y refresh tokens
- 🏢 **Multi-Tenancy**: Sistema de múltiples empresas por usuario con switch de tenant
- 👥 **Gestión de Clientes**: Búsqueda y consulta de deudores con cuotas vencidas
- 💳 **Registro de Pagos**: Control completo de transacciones con generación de recibos PDF
- 👤 **Gestión de Usuarios**: Sistema de usuarios protegido con roles (admin/standard)
- 📊 **Administración**: Endpoints para gestión de usuarios, empresas y bases de datos
- 🛡️ **Rate Limiting**: Protección contra abuse con límites por IP
- ✅ **Validaciones**: Datos validados con Pydantic
- 📝 **Documentación Auto-generada**: Swagger UI disponible
- 🧪 **Testing Unitario**: Cobertura completa con pytest
- 🌐 **Serverless Ready**: Optimizado para Vercel

## 🏗️ Arquitectura

El proyecto sigue la arquitectura recomendada por FastAPI:

```
app/
├── main.py              # Entry point de la aplicación
├── config.py           # Configuración centralizada (Pydantic Settings)
├── dependencies.py     # Dependencias reutilizables (JWT, DB)
├── database.py         # Conexiones a MySQL
├── mysql_db.py        # Funciones de base de datos
├── auth_utils.py      # Utilidades de autenticación
├── limiter.py         # Configuración de rate limiting
├── routers/           # Endpoints de la API
│   ├── auth.py
│   ├── clientes.py
│   ├── pagos.py
│   ├── usuarios.py
│   └── admin.py
├── schemas/           # Modelos Pydantic
├── services/          # Lógica de negocio
├── middleware/        # Middleware personalizado
└── models/           # Modelos de datos
```

## 📋 Requisitos

- Python 3.11+
- MySQL 8.0+
- PostgreSQL (opcional, para token blocklist)
- pip

## 🛠️ Instalación

### 1. Obtener el proyecto
```bash
git clone https://github.com/ElvinCooper/fast-payment.git
cd fast-payment
```

### 2. Crear entorno virtual
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Unix/MacOS
source venv/bin/activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno
```bash
cp .env.example .env
# Editar .env con tus credenciales
```

## ⚙️ Configuración

### Variables de Entorno

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `HOST` | Host del servidor MySQL | localhost |
| `PORT` | Puerto MySQL | 3306 |
| `DATABASE` | Base de datos por defecto | finanzasprueba |
| `USER` | Usuario MySQL | root |
| `DBPASSWORD` | Contraseña MySQL |password123 |
| `SECRET_KEY` | Clave secreta para JWT | tu_clave_segura |
| `EXPIRE_HOURS` | Horas de expiración del token | 2 |
| `POSTGRES_BD` | URL de PostgreSQL (opcional) | postgresql://... |

### Base de Datos Central (ciadatabase)

El sistema requiere una base de datos central `ciadatabase` con las siguientes tablas:

```sql
-- Empresas configuradas
CREATE TABLE ciasetup (
    idcia INT PRIMARY KEY,
    cidescripcion VARCHAR(255),
    descbd VARCHAR(255)
);

-- Usuarios del sistema
CREATE TABLE ciausers (
    idusers INT PRIMARY KEY,
    usuario VARCHAR(45) UNIQUE NOT NULL,
    clave VARCHAR(255) NOT NULL,
    estatus VARCHAR(10),
    tipouser VARCHAR(20),
    empresa_id INT,
    idcia INT
);

-- Relación usuario-empresa
CREATE TABLE userempresa (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    empresa_id INT
);

-- Token blocklist (PostgreSQL)
CREATE TABLE token_blocklist (
    id SERIAL PRIMARY KEY,
    jti VARCHAR(255) UNIQUE NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    idusuario INT
);
```

## 🌐 Endpoints API

### Autenticación
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `POST` | `/api/v1/auth/login` | Iniciar sesión y obtener token |
| `POST` | `/api/v1/auth/switch-tenant` | Cambiar de empresa activa |
| `POST` | `/api/v1/auth/refresh` | Refrescar token de acceso |

### Clientes 🔒
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/api/v1/clientes/` | Listar clientes |
| `GET` | `/api/v1/clientes/buscar` | Buscar clientes por nombre |
| `GET` | `/api/v1/clientes/{idcliente}` | Obtener cliente por ID |
| `GET` | `/api/v1/clientes/{idcliente}/cuotas-vencidas` | Cuotas vencidas del cliente |

### Pagos 🔒
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `POST` | `/api/v1/pagos/` | Registrar nuevo pago |
| `GET` | `/api/v1/pagos/generar-recibo` | Generar recibo PDF |

### Usuarios 🔒
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/api/v1/usuarios/me` | Obtener usuario actual |
| `POST` | `/api/v1/usuarios/logout` | Cerrar sesión (revocar token) |
| `POST` | `/api/v1/usuarios/refresh` | Refrescar token |

### Administración 🔒
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/api/v1/admin/users` | Listar usuarios de la empresa |
| `PUT` | `/api/v1/admin/user/cia` | Actualizar usuario (admin) |
| `GET` | `/api/v1/admin/user/tipos` | Listar tipos de usuario |
| `GET` | `/api/v1/admin/server/databases` | Listar bases de datos (admin) |
| `GET` | `/api/v1/admin/empresas` | Listar empresas del usuario |

🔒 *Requiere token JWT en el header: `Authorization: Bearer <token>`*

## 🏢 Sistema de Multi-Tenancy

El sistema soporta múltiples empresas por usuario:

1. **Login**: El usuario inicia sesión y recibe un token con la empresa por defecto
2. **Empresas**: Un usuario puede tener acceso a múltiples empresas
3. **Switch Tenant**: Cambio dinámico de empresa mediante `/auth/switch-tenant`
4. **Selección Obligatoria**: Si el usuario tiene >1 empresa, debe seleccionar una

### Flujo de Trabajo

```
1. Login → Token con empresa_id y db_name
2. Si tiene >1 empresa → requiere_selection: true
3. /auth/switch-tenant → Cambia empresa activa
4. Todas las queries usan la empresa seleccionada
```

## 📖 Ejemplos de Uso

### 1. Autenticación
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "usuario": "admin",
    "password": "admin123"
  }'
```

Respuesta:
```json
{
  "idusuario": 1,
  "username": "admin",
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "db_name": "finanzasprueba",
  "empresa": "Bio Finanzas Prueba"
}
```

### 2. Buscar Clientes
```bash
curl -X GET "http://localhost:8000/api/v1/clientes/buscar?nombre=Juan" \
  -H "Authorization: Bearer <tu_token>"
```

### 3. Registrar Pago
```bash
curl -X POST "http://localhost:8000/api/v1/pagos/" \
  -H "Authorization: Bearer <tu_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "idcliente": 724353,
    "cliente_nombre": "Juan Pérez",
    "monto": 2500.00,
    "idusuario": 9,
    "usuario_nombre": "Andrew"
  }'
```

### 4. Switch Tenant
```bash
curl -X POST "http://localhost:8000/api/v1/auth/switch-tenant" \
  -H "Authorization: Bearer <tu_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "empresa_id": 2
  }'
```

## 🧪 Testing

Ejecutar todos los tests:
```bash
pytest
```

Ejecutar tests con cobertura:
```bash
pytest --cov=app tests/ --cov-report=html
```

Ejecutar test específico:
```bash
pytest tests/test_pagos.py -v
```

## 🚀 Deployment

### Vercel (Recomendado)

1. Conectar repositorio a Vercel
2. Configurar variables de entorno en Vercel dashboard
3. Desplegar automáticamente con cada push

### Local
```bash
fastapi dev
# o
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

La documentación estará disponible en: `http://localhost:8000/docs`

## 📞 Contacto

- **Email**: ing.elvin01cooper@gmail.com
- **GitHub**: https://github.com/ElvinCooper/fast-payment

---

🔒 Proyecto privado - Todos los derechos reservados
