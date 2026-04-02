-- Crear base de datos ciadatabase si no existe
CREATE DATABASE IF NOT EXISTS ciadatabase;

USE ciadatabase;

-- Crear tabla ciausers si no existe
CREATE TABLE IF NOT EXISTS ciausers (
    idusers INT AUTO_INCREMENT PRIMARY KEY,
    usuario VARCHAR(255) NOT NULL,
    clave VARCHAR(255),
    estatus DECIMAL(1,0) DEFAULT 1,
    tipouser VARCHAR(50),
    empresa_id INT DEFAULT 1,
    idcia INT DEFAULT 1,
    INDEX idx_usuario (usuario),
    INDEX idx_idcia (idcia)
);

-- Crear tabla userempresa si no existe
CREATE TABLE IF NOT EXISTS userempresa (
    id INT AUTO_INCREMENT PRIMARY KEY,
    iduser INT NOT NULL,
    idcia INT NOT NULL,
    INDEX idx_iduser (iduser),
    INDEX idx_idcia (idcia)
);

-- Crear tabla ciasetup si no existe
CREATE TABLE IF NOT EXISTS ciasetup (
    idcia INT AUTO_INCREMENT PRIMARY KEY,
    cidescripcion VARCHAR(255),
    descbd VARCHAR(255),
    INDEX idx_descbd (descbd)
);

-- Insertar datos de prueba para ciasetup
INSERT INTO ciasetup (cidescripcion, descbd) VALUES 
    ('Bio Finanzas Prueba', 'finanzasprueba'),
    ('Bio Finanza Test', 'finanzastest')
ON DUPLICATE KEY UPDATE cidescripcion = cidescripcion;

-- Insertar datos de prueba para ciausers
INSERT INTO ciausers (usuario, clave, estatus, tipouser, empresa_id, idcia) VALUES 
    ('SUPERVISOR', 'ENTRADA', 1, 'admin', 1, 1)
ON DUPLICATE KEY UPDATE tipouser = tipouser;

-- Insertar datos de prueba para userempresa
INSERT INTO userempresa (iduser, idcia) VALUES 
    (1, 1),
    (1, 2)
ON DUPLICATE KEY UPDATE idcia = idcia;