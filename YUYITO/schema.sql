CREATE DATABASE IF NOT EXISTS AgendEx
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE AgendEx;

-- ------------------------------------------------------------
-- Tabla: cursos
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS cursos (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    nombre      VARCHAR(50)  NOT NULL UNIQUE,
    nivel       VARCHAR(30)  NOT NULL,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- Tabla: asignaturas (catálogo de materias)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS asignaturas (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    nombre      VARCHAR(80)  NOT NULL UNIQUE,
    color       VARCHAR(7)   DEFAULT '#3498db',
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- Tabla: profesores
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS profesores (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    nombre      VARCHAR(100) NOT NULL,
    apellido    VARCHAR(100) NOT NULL,
    email       VARCHAR(120) UNIQUE,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- Tabla: alumnos
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS alumnos (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    rut         VARCHAR(12)  NOT NULL UNIQUE,
    nombre      VARCHAR(80)  NOT NULL,
    apellido    VARCHAR(80)  NOT NULL,
    curso_id    INT          NOT NULL,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (curso_id) REFERENCES cursos(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- Tabla: usuarios (autenticación + roles)
-- Identificación por RUT (clave primaria, no se repite).
-- El inicio de sesión se hace con el CORREO institucional.
-- Roles: utp | profe | inspe | alumno
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS usuarios (
    rut          VARCHAR(12)  NOT NULL PRIMARY KEY,
    correo       VARCHAR(120) NOT NULL UNIQUE,
    clave        VARCHAR(255) NOT NULL,
    nombre       VARCHAR(120) NOT NULL,
    rol          ENUM('utp','profe','inspe','alumno') NOT NULL,
    profesor_id  INT NULL,
    alumno_id    INT NULL,
    activo       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (profesor_id) REFERENCES profesores(id) ON DELETE SET NULL,
    FOREIGN KEY (alumno_id)   REFERENCES alumnos(id)    ON DELETE SET NULL
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- Tabla: evaluaciones
-- Máximo 2 evaluaciones por curso en el mismo día
-- (garantizado por el procedimiento almacenado sp_crear_evaluacion)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS evaluaciones (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    titulo          VARCHAR(150) NOT NULL,
    fecha           DATE         NOT NULL,
    hora            TIME         NULL,
    descripcion     TEXT,
    asignatura_id   INT          NOT NULL,
    curso_id        INT          NOT NULL,
    profesor_id     INT          NOT NULL,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (asignatura_id) REFERENCES asignaturas(id) ON DELETE CASCADE,
    FOREIGN KEY (curso_id)      REFERENCES cursos(id)      ON DELETE CASCADE,
    FOREIGN KEY (profesor_id)   REFERENCES profesores(id)   ON DELETE CASCADE,
    INDEX idx_eval_fecha  (fecha),
    INDEX idx_eval_curso  (curso_id)
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- Tabla: asistencias (registro de ausencias por evaluación)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS asistencias (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    evaluacion_id   INT NOT NULL,
    alumno_id       INT NOT NULL,
    presente        BOOLEAN NOT NULL DEFAULT TRUE,
    motivo          VARCHAR(200),
    -- Solo Inspectoria (o UTP) marca si la ausencia fue justificada.
    -- Define la exigencia con la que el alumno rendira su recuperacion.
    justificado     BOOLEAN NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_eval_alumno (evaluacion_id, alumno_id),
    FOREIGN KEY (evaluacion_id) REFERENCES evaluaciones(id) ON DELETE CASCADE,
    FOREIGN KEY (alumno_id)     REFERENCES alumnos(id)      ON DELETE CASCADE
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- Tabla: recuperaciones (fechas de recuperación para ausentes)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS recuperaciones (
    id                  INT AUTO_INCREMENT PRIMARY KEY,
    evaluacion_id       INT  NOT NULL,
    alumno_id           INT  NOT NULL,
    fecha_recuperacion  DATE NOT NULL,
    motivo              VARCHAR(200),
    -- 60.00 = justificada (misma exigencia que el resto del curso)
    -- 70.00 = no justificada (mayor exigencia)
    porcentaje_exigencia DECIMAL(5,2) NOT NULL DEFAULT 70.00,
    estado              ENUM('pendiente','completada','cancelada') NOT NULL DEFAULT 'pendiente',
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (evaluacion_id) REFERENCES evaluaciones(id) ON DELETE CASCADE,
    FOREIGN KEY (alumno_id)     REFERENCES alumnos(id)      ON DELETE CASCADE
) ENGINE=InnoDB;

-- ============================================================
-- PROCEDIMIENTOS ALMACENADOS
-- La validación del límite de 2 evaluaciones por curso por día
-- se garantiza a nivel de BASE DE DATOS (Requerimiento R.4 y R.11)
-- ============================================================

DELIMITER $$

-- Verifica cuántas evaluaciones existen y cuántos espacios quedan
-- para un curso en una fecha determinada.
CREATE PROCEDURE sp_validar_disponibilidad(
    IN p_curso_id INT,
    IN p_fecha    DATE
)
BEGIN
    SELECT COUNT(*) AS existentes,
           2        AS maximo,
           2 - COUNT(*) AS disponibles
    FROM evaluaciones
    WHERE curso_id = p_curso_id AND fecha = p_fecha;
END$$

-- Crea una evaluación validando la política de máximo 2 por día.
-- Si ya existen 2 evaluaciones para el curso en esa fecha,
-- se lanza un error y NO se inserta el registro (integridad garantizada).
CREATE PROCEDURE sp_crear_evaluacion(
    IN p_titulo        VARCHAR(150),
    IN p_fecha         DATE,
    IN p_hora          TIME,
    IN p_descripcion   TEXT,
    IN p_asignatura_id INT,
    IN p_curso_id      INT,
    IN p_profesor_id   INT
)
BEGIN
    DECLARE v_count INT;

    IF p_fecha < CURDATE() THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'La fecha no puede ser anterior a la fecha actual.';
    END IF;

    SELECT COUNT(*) INTO v_count
    FROM evaluaciones
    WHERE curso_id = p_curso_id AND fecha = p_fecha;

    IF v_count >= 2 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Limite excedido: maximo 2 evaluaciones por curso por dia.';
    END IF;

    INSERT INTO evaluaciones
        (titulo, fecha, hora, descripcion, asignatura_id, curso_id, profesor_id)
    VALUES
        (p_titulo, p_fecha, p_hora, p_descripcion, p_asignatura_id, p_curso_id, p_profesor_id);

    SELECT LAST_INSERT_ID() AS id;
END$$

-- Actualiza una evaluación validando nuevamente el límite diario,
-- excluyendo la propia evaluación del conteo.
CREATE PROCEDURE sp_actualizar_evaluacion(
    IN p_id             INT,
    IN p_titulo         VARCHAR(150),
    IN p_fecha          DATE,
    IN p_hora           TIME,
    IN p_descripcion    TEXT,
    IN p_asignatura_id  INT,
    IN p_curso_id       INT,
    IN p_profesor_id    INT
)
BEGIN
    DECLARE v_count INT;

    IF p_fecha < CURDATE() THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'La fecha no puede ser anterior a la fecha actual.';
    END IF;

    SELECT COUNT(*) INTO v_count
    FROM evaluaciones
    WHERE curso_id = p_curso_id
      AND fecha = p_fecha
      AND id <> p_id;

    IF v_count >= 2 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Limite excedido: maximo 2 evaluaciones por curso por dia.';
    END IF;

    UPDATE evaluaciones
    SET titulo        = p_titulo,
        fecha         = p_fecha,
        hora          = p_hora,
        descripcion   = p_descripcion,
        asignatura_id = p_asignatura_id,
        curso_id      = p_curso_id,
        profesor_id   = p_profesor_id
    WHERE id = p_id;
END$$

-- Reporte de alumnos pendientes de recuperación de una evaluación
CREATE PROCEDURE sp_pendientes_recuperacion()
BEGIN
    SELECT r.id AS recuperacion_id,
           a.rut,
           a.nombre AS alumno_nombre,
           a.apellido AS alumno_apellido,
           c.nombre AS curso_nombre,
           e.titulo AS evaluacion,
           e.fecha AS fecha_original,
           r.fecha_recuperacion,
           r.motivo
    FROM recuperaciones r
    JOIN alumnos a ON a.id = r.alumno_id
    JOIN cursos c ON c.id = a.curso_id
    JOIN evaluaciones e ON e.id = r.evaluacion_id
    WHERE r.estado = 'pendiente'
    ORDER BY r.fecha_recuperacion;
END$$

DELIMITER ;
