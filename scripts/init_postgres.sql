-- Crear tabla mapeo_usuarios si no existe
CREATE TABLE IF NOT EXISTS mapeo_usuarios (
    idusuario INTEGER PRIMARY KEY,
    usuario VARCHAR(255),
    db_asignada VARCHAR(255),
    clave VARCHAR(255)
);

-- Crear tabla token_blocklist si no existe
CREATE TABLE IF NOT EXISTS token_blocklist (
    id SERIAL PRIMARY KEY,
    jti VARCHAR(36) NOT NULL,
    fecha_creacion DATE NOT NULL,
    idusuario INTEGER
);

-- Crear índices para búsquedas rápidas por jti
CREATE INDEX IF NOT EXISTS idx_token_blocklist_jti ON token_blocklist(jti);

-- Crear índice para búsquedas por usuario
CREATE INDEX IF NOT EXISTS idx_token_blocklist_usuario ON token_blocklist(idusuario);
