# 🚀 Fast Payment - Sistema de Cobros API

[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python)](https://www.python.org/)
[![MySQL](https://img.shields.io/badge/MySQL-8.0-blue?style=for-the-badge&logo=mysql)](https://www.mysql.com/)
[![JWT](https://img.shields.io/badge/JWT-Auth-red?style=for-the-badge&logo=jwt)](https://jwt.io/)

Una API REST robusta y moderna para la gestión de cobros y pagos de clientes, construida con FastAPI y diseñada para operar en entornos de producción serverless.

## 📋 Tabla de Contenido

- [Características](#-características)
- [Requisitos](#-requisitos)
- [Instalación](#-instalación)
- [Configuración](#-configuración)
- [Endpoints API](#-endpoints-api)
- [Ejemplos de Uso](#-ejemplos-de-uso)
- [Testing](#-testing)
- [Deployment](#-deployment)
- [Contribuir](#-contribuir)
- [Licencia](#-licencia)

## ✨ Características

- 🔐 **Autenticación JWT**: Tokens seguros con expiración automática
- 👥 **Gestión de Clientes**: Búsqueda y consulta de deudores
- 💳 **Registro de Pagos**: Control completo de transacciones
- 👤 **Gestión de Usuarios**: Sistema de usuarios protegido
- 🛡️ **Validaciones**: Datos validados con Pydantic
- 📝 **Documentación Auto-generada**: Swagger UI disponible
- 🧪 **Testing Unitario**: Cobertura completa de endpoints
- 🌐 **Serverless Ready**: Optimizado para Vercel

## 📋 Requisitos

- Python 3.11+
- MySQL 8.0+
- pip o poetry

## 🛠️ Instalación

### 1. Obtener el proyecto
```bash
# El proyecto es privado. Contacta al administrador para obtener acceso.
# Una vez tengas acceso:
git clone [URL-del-repositorio-privado]
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
Crea un archivo `.env` en la raíz del proyecto:

```env
# Database
HOST= tu_host_mysql
DATABASE= tu_base_de_datos
USER= tu_usuario
DBPASSWORD= tu_contraseña

# JWT
SECRET_KEY= tu_clave_secreta_super_segura_aqui
```

### Estructura de la Base de Datos

Asegúrate de tener las siguientes tablas:

```sql
-- Usuarios del sistema
CREATE TABLE usuario (
    idusuario INT PRIMARY KEY,
    usuario VARCHAR(45) UNIQUE NOT NULL,
    clave VARCHAR(45) NOT NULL
);

-- Clientes
CREATE TABLE cliente (
    idcliente INT PRIMARY KEY,
    CLIENTE VARCHAR(255) NOT NULL
);

-- Préstamos activos
CREATE TABLE prestamo (
    nprestamo INT PRIMARY KEY,
    vprestamo DECIMAL(10,2) NOT NULL,
    CODIGO INT,
    FOREIGN KEY (CODIGO) REFERENCES cliente(idcliente)
);

-- Registro de pagos
CREATE TABLE handheldata (
    id INT AUTO_INCREMENT PRIMARY KEY,
    codigo INT NOT NULL,
    Cliente VARCHAR(255) NOT NULL,
    Fecha DATE NOT NULL,
    Hora DATETIME NOT NULL,
    MontoPgdo DECIMAL(10,2) NOT NULL,
    nusuario INT NOT NULL,
    cusuario VARCHAR(45) NOT NULL
);
```

## 🌐 Endpoints API

### Autenticación
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `POST` | `/api/v1/auth/login` | Genera token de autenticación |

### Clientes 🔒
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/api/v1/clientes/buscar?nombre=` | Buscar clientes por nombre (LIKE) |
| `GET` | `/api/v1/clientes/{id}` | Obtener cliente por ID con préstamos |

### Pagos 🔒
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `POST` | `/api/v1/pagos/` | Registrar nuevo pago |

### Usuarios 🔒
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/api/v1/usuarios/{id}` | Obtener usuario por ID |

🔒 *Requiere token JWT en el header: `Authorization: Bearer <token>`*

## 📖 Ejemplos de Uso

### 1. Autenticación
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "usuario": "testuser",
    "password": "testpass"
  }'
```

Respuesta:
```json
{
  "idusuario": 1,
  "usuario": "testuser",
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "message": "Login exitoso"
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

## 🧪 Testing

Ejecutar todos los tests:
```bash
pytest
```

Ejecutar tests con cobertura:
```bash
pytest --cov=app tests/
```

Ejecutar test específico:
```bash
pytest tests/test_pagos.py -v
```

## 🚀 Deployment

### Vercel (Recomendado)

1. Instalar Vercel CLI:
```bash
npm i -g vercel
```

2. Desplegar:
```bash
vercel --prod
```

3. Configurar variables de entorno en Vercel dashboard

### Local
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

La documentación estará disponible en: `http://localhost:8000/docs`

## 🤝 Contribuir

Este proyecto es privado y no está aceptando contribuciones externas en este momento.

## 📝 Changelog

### [1.0.0] - 2024-01-XX
- ✨ Versión inicial
- ✨ Autenticación JWT
- ✨ Gestión de clientes y pagos
- ✨ Testing unitario completo
- ✨ Deploy en Vercel

## 📄 Licencia

Este proyecto es de uso privado y no está bajo ninguna licencia de código abierto.

## 📞 Contacto

- **Email**: ing.elvin01cooper@gmail.com

---

🔒 Proyecto privado - Todos los derechos reservados