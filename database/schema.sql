-- ============================================================
-- AgendEx · Sistema de Evaluaciones Escolares (Liceo RBL)
-- Esquema de Base de Datos MySQL
-- ============================================================

CREATE DATABASE IF NOT EXISTS agendex_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE agendex_db;

-- 1. Tabla de Cursos
CREATE TABLE IF NOT EXISTS cursos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(20) NOT NULL,
    nivel VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- 2. Tabla de Asignaturas
CREATE TABLE IF NOT EXISTS asignaturas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    color VARCHAR(20) DEFAULT '#14213D',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- 3. Tabla de Profesores
CREATE TABLE IF NOT EXISTS profesores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(60) NOT NULL,
    apellido VARCHAR(60) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    materia VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- 4. Tabla de Alumnos
CREATE TABLE IF NOT EXISTS alumnos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    rut VARCHAR(15) NOT NULL UNIQUE,
    nombre VARCHAR(60) NOT NULL,
    apellido VARCHAR(60) NOT NULL,
    curso_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (curso_id) REFERENCES cursos(id) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB;

-- 5. Tabla de Usuarios del Sistema
CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    rut VARCHAR(15) NOT NULL UNIQUE,
    correo VARCHAR(100) NOT NULL UNIQUE,
    clave VARCHAR(255) NOT NULL,
    nombre VARCHAR(120) NOT NULL,
    rol ENUM('utp', 'profe', 'inspe', 'alumno') NOT NULL,
    profesor_id INT DEFAULT NULL,
    alumno_id INT DEFAULT NULL,
    activo TINYINT(1) DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (profesor_id) REFERENCES profesores(id) ON DELETE SET NULL ON UPDATE CASCADE,
    FOREIGN KEY (alumno_id) REFERENCES alumnos(id) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB;

-- 6. Tabla de Evaluaciones
CREATE TABLE IF NOT EXISTS evaluaciones (
    id INT AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(150) NOT NULL,
    descripcion TEXT,
    fecha DATE NOT NULL,
    hora TIME DEFAULT NULL,
    asignatura_id INT NOT NULL,
    curso_id INT NOT NULL,
    profesor_id INT NOT NULL,
    asistencia_guardada TINYINT(1) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (asignatura_id) REFERENCES asignaturas(id) ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY (curso_id) REFERENCES cursos(id) ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY (profesor_id) REFERENCES profesores(id) ON DELETE RESTRICT ON UPDATE CASCADE,
    INDEX idx_curso_fecha (curso_id, fecha)
) ENGINE=InnoDB;

-- 7. Tabla de Asistencia a Evaluaciones
CREATE TABLE IF NOT EXISTS asistencia_evaluaciones (
    id INT AUTO_INCREMENT PRIMARY KEY,
    evaluacion_id INT NOT NULL,
    alumno_id INT NOT NULL,
    estado_asistencia ENUM('presente', 'injustificada', 'justificado', 'salida') DEFAULT 'presente',
    presente TINYINT(1) NOT NULL DEFAULT 1,
    justificado TINYINT(1) DEFAULT 0,
    motivo_inasistencia VARCHAR(255) DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_eval_alumno (evaluacion_id, alumno_id),
    FOREIGN KEY (evaluacion_id) REFERENCES evaluaciones(id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (alumno_id) REFERENCES alumnos(id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

-- 8. Tabla de Evaluaciones de Recuperación
CREATE TABLE IF NOT EXISTS recuperaciones (
    id INT AUTO_INCREMENT PRIMARY KEY,
    evaluacion_id INT NOT NULL,
    alumno_id INT NOT NULL,
    fecha_recuperacion DATE NOT NULL,
    motivo VARCHAR(255),
    exigencia DECIMAL(5,2) NOT NULL DEFAULT 60.00,
    estado ENUM('pendiente', 'rendida', 'cancelada') DEFAULT 'pendiente',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (evaluacion_id) REFERENCES evaluaciones(id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (alumno_id) REFERENCES alumnos(id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ============================================================
-- PROCEDIMIENTOS ALMACENADOS
-- ============================================================

DROP PROCEDURE IF EXISTS sp_validar_disponibilidad;
DELIMITER $$
CREATE PROCEDURE sp_validar_disponibilidad(
    IN p_curso_id INT,
    IN p_fecha DATE,
    OUT p_disponible TINYINT(1),
    OUT p_total INT
)
BEGIN
    SELECT COUNT(*) INTO p_total
    FROM evaluaciones
    WHERE curso_id = p_curso_id AND fecha = p_fecha;

    IF p_total < 2 THEN
        SET p_disponible = 1;
    ELSE
        SET p_disponible = 0;
    END IF;
END$$
DELIMITER ;

DROP PROCEDURE IF EXISTS sp_crear_evaluacion;
DELIMITER $$
CREATE PROCEDURE sp_crear_evaluacion(
    IN p_titulo VARCHAR(150),
    IN p_descripcion TEXT,
    IN p_fecha DATE,
    IN p_hora TIME,
    IN p_asignatura_id INT,
    IN p_curso_id INT,
    IN p_profesor_id INT,
    OUT p_evaluacion_id INT
)
BEGIN
    DECLARE v_total INT;

    SELECT COUNT(*) INTO v_total
    FROM evaluaciones
    WHERE curso_id = p_curso_id AND fecha = p_fecha;

    IF v_total >= 2 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Límite máximo de 2 evaluaciones diarias alcanzado para este curso.';
    ELSE
        INSERT INTO evaluaciones (titulo, descripcion, fecha, hora, asignatura_id, curso_id, profesor_id)
        VALUES (p_titulo, p_descripcion, p_fecha, p_hora, p_asignatura_id, p_curso_id, p_profesor_id);

        SET p_evaluacion_id = LAST_INSERT_ID();
    END IF;
END$$
DELIMITER ;
