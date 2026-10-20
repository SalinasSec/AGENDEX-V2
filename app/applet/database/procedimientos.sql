USE agendex_db;

DELIMITER $$

-- ------------------------------------------------------------------------
-- PROCEDIMIENTO 1: sp_verificar_cupo_evaluacion
-- ------------------------------------------------------------------------
-- PROPÓSITO:
--   Verifica si un curso tiene cupo disponible para calendarizar una nueva
--   evaluación en una fecha específica, respetando la Regla Institucional:
--   "Máximo 2 evaluaciones por curso en un mismo día".
--
-- PARÁMETROS:
--   IN  p_curso_id   INT      : ID del curso a consultar.
--   IN  p_fecha      DATE     : Fecha de la prueba a calendarizar.
--   OUT p_total      INT      : Cantidad de pruebas ya agendadas ese día.
--   OUT p_disponible TINYINT  : 1 si hay cupo (total < 2), 0 si está bloqueado.
-- ------------------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_verificar_cupo_evaluacion$$
CREATE PROCEDURE sp_verificar_cupo_evaluacion(
    IN  p_curso_id   INT,
    IN  p_fecha      DATE,
    OUT p_total      INT,
    OUT p_disponible TINYINT(1)
)
BEGIN
    -- Contar las evaluaciones existentes para el curso en la fecha indicada
    SELECT COUNT(*) INTO p_total
    FROM evaluaciones
    WHERE curso_id = p_curso_id AND fecha = p_fecha;

    -- Si hay menos de 2, hay disponibilidad (1); de lo contrario, se bloquea (0)
    IF p_total < 2 THEN
        SET p_disponible = 1;
    ELSE
        SET p_disponible = 0;
    END IF;
END$$

-- ------------------------------------------------------------------------
-- PROCEDIMIENTO 2: sp_registrar_asistencia_estudiante
-- ------------------------------------------------------------------------
-- PROPÓSITO:
--   Registra o actualiza la asistencia de un alumno a una evaluación.
--   Aplica la lógica institucional de negocio de forma atómica:
--   1. Si el alumno está 'presente': no genera citación a prueba recuperativa.
--   2. Si faltó con 'injustificada': genera/actualiza citación a recuperativa
--      con 70% de exigencia.
--   3. Si tiene 'justificado' (médico) o 'salida' (pedagógica): fija la
--      exigencia al 60% regular.
--
-- PARÁMETROS:
--   IN p_eval_id     INT          : ID de la evaluación.
--   IN p_alumno_id   INT          : ID del estudiante.
--   IN p_estado      VARCHAR(20)  : 'presente', 'injustificada', 'justificado', 'salida'.
--   IN p_motivo      VARCHAR(255) : Observación o folio de certificado médico.
-- ------------------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_registrar_asistencia_estudiante$$
CREATE PROCEDURE sp_registrar_asistencia_estudiante(
    IN p_eval_id   INT,
    IN p_alumno_id INT,
    IN p_estado    VARCHAR(20),
    IN p_motivo    VARCHAR(255)
)
BEGIN
    DECLARE v_presente TINYINT(1);
    DECLARE v_justificado TINYINT(1);
    DECLARE v_exigencia DECIMAL(5,2);
    DECLARE v_motivo_recup VARCHAR(255);
    DECLARE v_recup_id INT;

    -- Normalizar estado
    IF p_estado IS NULL OR p_estado = '' THEN
        SET p_estado = 'presente';
    END IF;

    -- Determinar flags booleanos
    IF p_estado = 'presente' THEN
        SET v_presente = 1;
        SET v_justificado = 0;
    ELSEIF p_estado = 'injustificada' THEN
        SET v_presente = 0;
        SET v_justificado = 0;
        SET v_exigencia = 70.00;
        SET v_motivo_recup = IF(p_motivo IS NOT NULL AND p_motivo != '', p_motivo, 'Inasistencia sin justificar');
    ELSE
        -- 'justificado' (médico) o 'salida' (pedagógica)
        SET v_presente = 0;
        SET v_justificado = 1;
        SET v_exigencia = 60.00;
        IF p_estado = 'salida' THEN
            SET v_motivo_recup = IF(p_motivo IS NOT NULL AND p_motivo != '', p_motivo, 'Salida Pedagógica Oficial');
        ELSE
            SET v_motivo_recup = IF(p_motivo IS NOT NULL AND p_motivo != '', p_motivo, 'Certificado Médico Acreditado');
        END IF;
    END IF;

    -- 1. Insertar o actualizar registro de asistencia
    INSERT INTO asistencia_evaluaciones (
        evaluacion_id, alumno_id, estado_asistencia, presente, justificado, motivo_inasistencia
    )
    VALUES (
        p_eval_id, p_alumno_id, p_estado, v_presente, v_justificado, p_motivo
    )
    ON DUPLICATE KEY UPDATE
        estado_asistencia   = VALUES(estado_asistencia),
        presente            = VALUES(presente),
        justificado         = VALUES(justificado),
        motivo_inasistencia = VALUES(motivo_inasistencia);

    -- 2. Si el alumno estuvo ausente, asegurar la prueba de recuperación con su exigencia
    IF v_presente = 0 THEN
        SELECT id INTO v_recup_id
        FROM recuperaciones
        WHERE evaluacion_id = p_eval_id AND alumno_id = p_alumno_id
        LIMIT 1;

        IF v_recup_id IS NOT NULL THEN
            UPDATE recuperaciones
            SET exigencia = v_exigencia,
                motivo = v_motivo_recup,
                estado = 'pendiente'
            WHERE id = v_recup_id;
        ELSE
            INSERT INTO recuperaciones (
                evaluacion_id, alumno_id, fecha_recuperacion, motivo, exigencia, estado
            )
            VALUES (
                p_eval_id, p_alumno_id, DATE_ADD(CURDATE(), INTERVAL 7 DAY), v_motivo_recup, v_exigencia, 'pendiente'
            );
        END IF;
    END IF;
END$$

-- ------------------------------------------------------------------------
-- PROCEDIMIENTO 3: sp_resumen_carga_curso
-- ------------------------------------------------------------------------
-- PROPÓSITO:
--   Calcula la cantidad total de evaluaciones de un curso en un mes dado
--   y determina si el curso se encuentra en condición de "Alta Carga"
--   (6 o más evaluaciones mensuales de distintas asignaturas).
--
-- PARÁMETROS:
--   IN  p_curso_id      INT         : ID del curso.
--   IN  p_mes           INT         : Mes (1 al 12).
--   IN  p_anio          INT         : Año (ej. 2026).
--   OUT p_total_evals   INT         : Total de pruebas programadas en el mes.
--   OUT p_alta_carga    TINYINT(1)  : 1 si tiene 6 o más pruebas, 0 en caso contrario.
-- ------------------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_resumen_carga_curso$$
CREATE PROCEDURE sp_resumen_carga_curso(
    IN  p_curso_id    INT,
    IN  p_mes         INT,
    IN  p_anio        INT,
    OUT p_total_evals INT,
    OUT p_alta_carga  TINYINT(1)
)
BEGIN
    SELECT COUNT(*) INTO p_total_evals
    FROM evaluaciones
    WHERE curso_id = p_curso_id
      AND MONTH(fecha) = p_mes
      AND YEAR(fecha) = p_anio;

    IF p_total_evals >= 6 THEN
        SET p_alta_carga = 1;
    ELSE
        SET p_alta_carga = 0;
    END IF;
END$$

DELIMITER ;
